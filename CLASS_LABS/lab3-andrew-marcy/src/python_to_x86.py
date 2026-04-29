from x86_IR import *


def asm_prologue():
    return f""".globl main
main:
    pushl %ebp ## save caller's base pointer
    movl %esp, %ebp ## set our base pointer
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

def is_numeric(s):
    try:
        float(s) 
        return True
    except ValueError:
        return False


def format_loc(loc):
        if "(" in loc:
            return loc
        if is_numeric(loc):
            return f"${loc}"
        return f"%{loc}"

def is_stack_ref(target):
    return "(" in target

class X86Instruction:
    def __init__(self, type, src, dest):
        self.type = type
        self.src = src
        self.dest = dest
        self.IR_src = ""
        self.IR_dest = ""
        self.IR_index = 0
    def __repr__(self):
        return f"{self.type} {self.IR_src} {self.IR_dest} [{self.type} {self.src}, {self.dest}]"


class X86InstructionList:
    
    def __init__(self, IR, reg_alloc):
        
        self.lst = []
        self.IR = IR
        self.INTEGER_SIZE = 4
        self.reg_alloc = reg_alloc
        self.populate_list()

    def get_double_stack_ref_instructions(self):
        res = []
        for instr in self.lst:
            if instr.type == "movl" or instr.type == "addl":
                if is_stack_ref(instr.src) and is_stack_ref(instr.dest):
                    res.append(instr)
        return res

    def populate_list(self):

        i = 0

        for instr in self.IR:

            if isinstance(instr, IR_movl) or isinstance(instr, IR_addl):

                s = instr.src
                t = instr.dest

                if is_numeric(s):
                    src = f"{s}"
                else:
                    src = self.reg_alloc.get_home(s)
                dest = self.reg_alloc.get_home(t)

                command = "movl" if isinstance(instr, IR_movl) else "addl"

                x86_instr = X86Instruction(command, src, dest)
                
                # special case when both operands are
                # stack references and need to be replaced
                # with temp variables in the IR, so
                # we keep track of the orginal IR src and dest names
                # so that they can be replaced in the IR

                if (is_stack_ref(src) and is_stack_ref(dest)):
                    x86_instr.IR_src = s
                    x86_instr.IR_dest = t
                    x86_instr.IR_index = i

                self.lst.append(x86_instr)

            elif isinstance(instr, IR_negl):
                
                s = instr.src
                src = self.reg_alloc.get_home(s)

                self.lst.append(X86Instruction("negl", src, ""))


            elif isinstance(instr, IR_call):

                if instr.id == "print":

                    s = instr.args

                    if is_numeric(s):
                        src = str(s)
                    else:
                        src = self.reg_alloc.get_home(instr.args)

                    self.lst.append(X86Instruction("movl", src, "eax"))
                    self.lst.append(X86Instruction("pushl", "eax", ""))
                    self.lst.append(X86Instruction("call", "print_int_nl", ""))
                    self.lst.append(X86Instruction("addl", f"{self.INTEGER_SIZE}", "esp"))

                elif instr.id == "eval_input":

                    self.lst.append(X86Instruction("call", "eval_input_int", ""))

                    if instr.args != "":

                        dest = self.reg_alloc.get_home(instr.args)
                        
                        self.lst.append(X86Instruction("movl", "eax", dest))
            i += 1

class X86CodeGenerator:

    def __init__(self, instruction_list):

        self.instruction_list = instruction_list
        self.space = "    "

    def generate_x86_asm_code(self):
    
        x86_code = "\n"

        for instruction in self.instruction_list:
            x86_code += self.space + self.to_x86_line_code(instruction) + "\n"

        return x86_code


    def to_x86_line_code(self, instr):

        if instr.type == "movl" or instr.type == "addl":
            return f"{instr.type} {format_loc(instr.src)}, {format_loc(instr.dest)}"

        elif instr.type == "negl":
            return f"negl {format_loc(instr.src)}"

        elif instr.type == "call":
            return f"call {instr.src}"

        elif instr.type == "pushl":
            return f"pushl {format_loc(instr.src)}"

        else:
            print(f"ERR : To_X86() unidentified command type {instr.type}")

        


def python_to_x86_asm(instr_list):

    x86_writer = X86CodeGenerator(instr_list.lst)

    x86_code = x86_writer.generate_x86_asm_code()

    return asm_prologue() + f"{x86_code}" + asm_epilogue()