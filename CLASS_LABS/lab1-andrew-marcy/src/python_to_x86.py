
import re
import ast
from ast import *
from flatten import *
from unparser import *



def asm_prologue(local_var_bytes):
    return f""".globl main
main:
    pushl %ebp ## save caller's base pointer
    movl %esp, %ebp ## set our base pointer
    subl ${local_var_bytes}, %esp ## allocate for local vars
    pushl %ebx ## save callee saved registers
    pushl %esi
    pushl %edi
"""



def asm_epilogue():
    return """
    popl %edi ## restore callee saved registers
    popl %esi
    popl %ebx
    movl $0, %eax ## set return value
    movl %ebp, %esp ## restore esp
    popl %ebp ## restore ebp (alt. “leave”)
    ret ## jump execution to call site
    """



# different types of simple statements
# WARNING : the following conditions
# only work correctly on flattened P0 programs
#=============================================

def is_assign_addition(line):
    return "=" in line and "+" in line

def is_assign_unary_sub(line):
    return "=" in line and "-" in line

def is_assign_eval_input(line):
    return "=" in line and "eval(input())" in line

def is_print(line):
    return "print" in line

def is_no_assignment_expression(line):
    return not "=" in line

def is_no_assign_eval_input(line):
    return line == "eval(input())"

def is_assign_atomic(line):
    if "=" in line:
        if "+" not in line and "-" not in line:
            return "eval(input())" not in line and "print" not in line

#=============================================


def get_assign_r_value(line):
    if is_assign_atomic(line):
        match = re.search(r'=\s*(\S+)', line)
        if match:
            return match.group(1)
        printf(f"ERR: regex could not find the r_value in {line}")
    else:
        print(f"ERR: attempted to extract r_value from NON-simple assign_statement {line}")


def get_assign_l_value(line):
    match = re.search(r'\s*(\S+)\s+', line)
    if match:
        return match.group(1)
    print(f"ERR: could not find l_value in line {line}")



def get_unary_sub_operand(line):
    if not is_assign_unary_sub(line):
        return
        printf(f"ERR : attemping to parse non-unary-sub assignment op as an unary-sub assignment op")
    match = re.search('=\s*-\((\S+)\)', line)
    if match:
        return match.group(1)
    else:
        print(f"ERR : could not find operand in unary sub operation {line}")



def get_sum_operands(line):
    if not is_assign_addition(line):
        printf(f"ERR : attemping to parse non-addition assignment op as an addition op")
        return
    match = re.search(r'=\s*(\S+)\s+\+\s+(\S+)', line)
    if match:
        return match.group(1), match.group(2)
    else:
        printf(f"ERR : could not find distinct operands in \'addition\' operation: \'{line}\'")



def get_single_print_arg(line):
    if not is_print(line):
        printf(f"ERR : attemping to parse non-print statement as print statement")
        return
    match = re.search(r'print\((\S+)\)', line)
    if match:
        return match.group(1)
    else:
        print(f"ERR : could not find argument in print statement : {line}")



# formats an assembly memory offset
def f(offset):
    if offset == 0:
        return ""
    else:
        return f"-{offset}"



#=====================================================

# The following class generates x86 assembly code line by line from flattened python source code
# consisting only of simple operations (e.g x = 1, x = 1 + 2, x = -1, x = -1 + 2, print(x))
# The class keeps track of which variable is stored at what offset. The allocate_var() method
# doesn't really "allocate" a new variable so to speak, but adds the variable to the known variable map
# with the variable's stack address offset

class ASMGenerator:

    def __init__(self):

        self.current_stack_head = 0
        self.stack_var_offsets = {}
        self.INTEGER_SIZE = 4
        self.space = "    "

    def generate_x86_asm_code(self, py_prog_flat):

        x86_asm_code = "\n\n"

        for line in py_prog_flat.splitlines():
            x86_asm_code += self.get_x86_line_code(line)
        
        return x86_asm_code

    def is_allocated(self, l_val):
        return l_val in self.stack_var_offsets

    def allocate_var(self, l_val):
        self.stack_var_offsets[l_val] = self.current_stack_head
        self.current_stack_head += self.INTEGER_SIZE

    def exit_alloc_error(self, l_val):
        print(f"ERR : The value of variable \'{l_val}\' is being used, but was never allocated in stack_var_offsets")
        exit(1)
    
    def get_offset(self, l_val):
        if self.is_allocated(l_val):
            return self.stack_var_offsets[l_val]
        self.exit_alloc_error(l_val)
        

    def get_x86_line_code(self, line):

        x86_line_code = ""

        if (is_assign_atomic(line)): # eg. temp_1 = 100, or temp_1 = temp_2

            print(f"Line : {line} (Assign-ATOMIC)")

            l_val = get_assign_l_value(line)
            r_val = get_assign_r_value(line)

            if not self.is_allocated(l_val):
                self.allocate_var(l_val)


            if r_val.isnumeric():

                offset = self.get_offset(l_val)
                s1 = f"movl ${int(r_val)}, {f(offset)}(%ebp)\n"
                x86_line_code += (self.space + s1 + "\n")

            else:

                #r_val is a variable

                if not self.is_allocated(r_val):
                    self.exit_alloc_error(r_val)

                offset_r = self.get_offset(r_val)
                offset_l = self.get_offset(l_val)

                s1 = f"movl {f(offset_r)}(%ebp), %eax\n"
                s2 = f"movl %eax, {f(offset_l)}(%ebp)\n"
                
                x86_line_code += (self.space + s1)
                x86_line_code += (self.space + s2)
                x86_line_code += "\n"


        elif (is_assign_addition(line)): # eg. temp_1 = a + b 

            print(f"Line : {line} (Assign-ADD)")

            l_val = get_assign_l_value(line)

            if not self.is_allocated(l_val):
                self.allocate_var(l_val)

            offset_l = self.get_offset(l_val)
            op_1, op_2 = get_sum_operands(line)

            if op_1.isnumeric() and op_2.isnumeric():

                s1 = f"movl ${int(op_1)}, %eax\n"
                s2 = f"addl ${int(op_2)}, %eax\n"
                s3 = f"movl %eax, {f(offset_l)}(%ebp)\n"
                
            elif op_1.isnumeric():

                offset_r = self.get_offset(op_2)
                
                s1 = f"movl ${int(op_1)}, %eax\n"
                s2 = f"addl {f(offset_r)}(%ebp), %eax\n"
                s3 = f"movl %eax, {f(offset_l)}(%ebp)\n"

            elif op_2.isnumeric():

                offset_r = self.get_offset(op_1)
                
                s1 = f"movl ${int(op_2)}, %eax\n"
                s2 = f"addl {f(offset_r)}(%ebp), %eax\n"
                s3 = f"movl %eax, {f(offset_l)}(%ebp)\n"

            else:
                
                offset_r1 = self.get_offset(op_1)
                offset_r2 = self.get_offset(op_2)

                s1 = f"movl {f(offset_r1)}(%ebp), %eax\n"
                s2 = f"addl {f(offset_r2)}(%ebp), %eax\n"
                s3 = f"movl %eax, {f(offset_l)}(%ebp)\n"
            
            x86_line_code += (self.space + s1)
            x86_line_code += (self.space + s2)
            x86_line_code += (self.space + s3)
            x86_line_code += "\n"


        elif (is_assign_unary_sub(line)):

            print(f"Line : {line} (Assign-USub)")

            l_val = get_assign_l_value(line)
            
            if not self.is_allocated(l_val):
                self.allocate_var(l_val)
            
            offset_l = self.get_offset(l_val)
            op = get_unary_sub_operand(line)

            if op.isnumeric():

                s1 = f"movl ${int(op)}, {f(offset_l)}(%ebp)\n"
                s2 = f"negl {f(offset_l)}(%ebp)\n"

                x86_line_code += (self.space + s1)
                x86_line_code += (self.space + s2)
                x86_line_code += "\n"
            
            else:

                offset_r = self.get_offset(op)

                s1 = f"movl {f(offset_r)}(%ebp), %eax\n"
                s2 = f"negl %eax\n"
                s3 = f"movl %eax, {f(offset_l)}(%ebp)\n"

                x86_line_code += (self.space + s1)
                x86_line_code += (self.space + s2)
                x86_line_code += (self.space + s3)
                x86_line_code += "\n"


        elif (is_assign_eval_input(line)):

            print(f"Line : {line} (Assign-EVAL-INPUT)")

            l_val = get_assign_l_value(line)

            if not self.is_allocated(l_val):
                self.allocate_var(l_val)
            
            offset_l = self.get_offset(l_val)

            s1 = f"call eval_input_int\n"
            s2 = f"movl %eax, {f(offset_l)}(%ebp)\n"

            x86_line_code += (self.space + s1)
            x86_line_code += (self.space + s2)
            x86_line_code += "\n"
        
        elif (is_no_assign_eval_input(line)):

            print(f"Line : {line} (NO-ASSIGN INPUT)")

            s1 = f"call eval_input_int\n"
            
            x86_line_code += (self.space + s1)
            x86_line_code += "\n"

        elif (is_print(line)):

            print(f"Line : {line} (PRINT)")

            arg = get_single_print_arg(line)

            if arg.isnumeric():
                s1 = f"movl ${int(arg)}, %eax\n"
                
            else:
                offset_r = self.get_offset(arg)
                s1 = f"movl {f(offset_r)}(%ebp), %eax\n"

            s2 = f"pushl %eax\n"
            s3 = f"call print_int_nl\n"
            s4 = f"addl $4, %esp\n"

            x86_line_code += (self.space + s1)
            x86_line_code += (self.space + s2)
            x86_line_code += (self.space + s3)
            x86_line_code += (self.space + s4)
            x86_line_code += "\n"

        elif (is_no_assignment_expression(line)):

            print(f"Line : {line} (Expression - No Assignment (NO IMPACT))")

        else:
            
            print(f"ERR: UNIDENTIFIED STATEMENT : {line}")
            exit(0)

        return x86_line_code




def to_x86(py_prog_flat):
    asm_generator = ASMGenerator()
    asm_code = asm_generator.generate_x86_asm_code(py_prog_flat)
    return f"{asm_code}"





def python_to_x86_asm(py_prog):
    
    py_prog_AST = ast.parse(py_prog)

    print("\n\nCOMPILING the following python3 program")
    print("======================================")
    print(py_prog, end="")
    print("======================================")

    RenameVariables().visit(py_prog_AST)
    py_prog_AST_FLAT = flatten_ast(py_prog_AST)
    py_prog_flat = UnParser().un_parse(py_prog_AST_FLAT)

    print("\n\nFlattened code")
    print("======================================")
    print(py_prog_flat, end="")
    print("======================================")
    

    local_vars = get_local_vars(py_prog_AST_FLAT)
    local_var_bytes = len(local_vars) * 4

    print(f"\n\nLocal variables ({len(local_vars)}) : {local_vars}")
    print(f"Local variable stack space required (bytes) : {local_var_bytes}")


    x86_asm_code = asm_prologue(local_var_bytes) + to_x86(py_prog_flat) + asm_epilogue()


    print("\n\nx86_ASM code generated")
    print("======================================")
    print(x86_asm_code)
    print("======================================")


    return x86_asm_code