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
    if is_numeric(loc):
        return f"${loc}"
    if "(" in loc:
        return loc
    return f"%{loc}"

def is_stack_ref(target):
    return "(" in target

class X86Instruction:
    def __init__(self, type, src, dest):
        self.type = type
        self.src = src
        self.dest = dest
    def __repr__(self):
        return f"{self.type} {self.src}, {self.dest}"


class X86InstructionList:
    
    def __init__(self, IR, reg_alloc):
        
        self.lst = []
        self.IR = IR
        self.INTEGER_SIZE = 4
        self.reg_alloc = reg_alloc
        self.populate_list()

    def get_double_stack_ref_instructions(self):
        res = {}
        for i in range(len(self.lst)):
            instr = self.lst[i]
            if instr.type == "movl" or instr.type == "addl":
                if is_stack_ref(instr.src) and is_stack_ref(instr.dest):
                    res[instr] = i
        return res
    
    def get_movzbl_stack_ref_instructions(self):
        res = {}
        for i in range(len(self.lst)):
            instr = self.lst[i]
            if instr.type == "movzbl":
                if is_stack_ref(instr.dest):
                    res[instr] = i
        return res
    
    def get_spill_required_instructions(self):
        double_stack_instrs = self.get_double_stack_ref_instructions()
        movzbl_stack_instrs = self.get_movzbl_stack_ref_instructions()
        spill_req_instrs = double_stack_instrs | movzbl_stack_instrs
        return dict(sorted(spill_req_instrs.items(), key=lambda item: item[1]))

    def populate_list(self):

        i = 0

        for instr in self.IR.get_instruction_list():

            if isinstance(instr, IR_movl) or isinstance(instr, IR_addl):

                s = instr.src
                t = instr.dest

                if is_numeric(s):
                    src = f"{s}"
                else:
                    src = self.reg_alloc.get_home(s)
                dest = self.reg_alloc.get_home(t)

                command = "movl" if isinstance(instr, IR_movl) else "addl"
                
                self.lst.append(X86Instruction(command, src, dest))

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
            
            elif isinstance(instr, IR_cmpl):

                left = instr.left
                right = instr.right

                if is_numeric(left):
                    src = left
                else:
                    src = self.reg_alloc.get_home(instr.left)

                dest = self.reg_alloc.get_home(instr.right)

                self.lst.append(X86Instruction("cmpl", src, dest))

            elif isinstance(instr, IR_sete):

                self.lst.append(X86Instruction("sete", "al", ""))
            
            elif isinstance(instr, IR_setne):

                self.lst.append(X86Instruction("setne", "al", ""))

            elif isinstance(instr, IR_movzbl):
                
                # movzbl instructions could potentially produce spills
                # keep track of their position in the IR instruction list
                
                dest = self.reg_alloc.get_home(instr.dest)                
                x86_instr = X86Instruction("movzbl", "al", dest)
                # x86_instr.IR_index = i

                self.lst.append(x86_instr)

            elif isinstance(instr, IR_je):

                self.lst.append(X86Instruction("je", instr.label, ""))

            elif isinstance(instr, IR_jmp):

                self.lst.append(X86Instruction("jmp", instr.label, ""))

            elif isinstance(instr, IR_label):

                self.lst.append(X86Instruction(instr.label, "", ""))
            else:

                print("ERR : unrecognized instruction in X86InstructionList")
                exit(0)

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

        elif instr.type == "cmpl":
            return f"cmpl {format_loc(instr.src)}, {format_loc(instr.dest)}"
        
        elif instr.type == "sete":
            return f"sete {format_loc(instr.src)}"
        
        elif instr.type == "setne":
            return f"setne {format_loc(instr.src)}"
        
        elif instr.type == "movzbl":
            return f"movzbl {format_loc(instr.src)}, {format_loc(instr.dest)}"
        
        elif instr.type == "je":
            return f"je {instr.src}"

        elif instr.type == "jmp":
            return f"jmp {instr.src}"

        else: # is x86 label
            return f"\n{self.space}{instr.type}:"
        


def python_to_x86_asm(instr_list):

    x86_writer = X86CodeGenerator(instr_list.lst)

    x86_code = x86_writer.generate_x86_asm_code()

    return asm_prologue() + f"{x86_code}" + asm_epilogue()