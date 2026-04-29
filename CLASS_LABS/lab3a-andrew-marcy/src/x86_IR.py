from unparser import *

INDENT = "    "

def is_eval_input(s):
    return "eval" in s


def is_print(s):
    return "print" in s


def is_numeric(s):
    try:
        float(s) 
        return True
    except ValueError:
        return False


def to_str(atomic):
    if isinstance(atomic, ast.Name):
        return atomic.id
    if isinstance(atomic, ast.Constant):
        return atomic.value
    

def add_to_list_unique(lst, look_up_set, elem):
    if elem not in look_up_set:
        lst.append(elem)
        look_up_set.add(elem)


class IR_movl:
    def __init__(self, src, dest, indent=0, spill_code=False):
        self.src = str(src)
        self.dest = str(dest)
        self.spill_code = spill_code
        self.indent = indent
    def __repr__(self):
        if self.spill_code:
            return f"{INDENT * self.indent}\033[1mmovl {self.src}, {self.dest}\033[0m"
        else:
            return f"{INDENT * self.indent}movl {self.src}, {self.dest}"

class IR_addl:
    def __init__(self, src, dest, indent=0, spill_code=False):
        self.src = str(src)
        self.dest = str(dest)
        self.spill_code = spill_code
        self.indent = indent
    def __repr__(self):
        if self.spill_code:
            return f"{INDENT * self.indent}\033[1maddl {self.src}, {self.dest}\033[0m"
        else:
            return f"{INDENT * self.indent}addl {self.src}, {self.dest}"

class IR_negl:
    def __init__(self, src, indent=0):
        self.src = str(src)
        self.indent = indent
    def __repr__(self):
        return f"{INDENT * self.indent}negl {self.src}"

class IR_call:
    def __init__(self, id, args, indent=0):
        self.id = id
        self.args = args
        self.indent = indent
    def __repr__(self):
        if self.id == "eval_input":
            return f"{INDENT * self.indent}eval_input {self.args}"
        if self.id == "print":
            return f"{INDENT * self.indent}print {self.args}"

class IR_cmpl:
    def __init__(self, left, right, indent=0):
        self.left = left
        self.right = right
        self.indent = indent
    def __repr__(self):
        return f"{INDENT * self.indent}cmpl {self.left}, {self.right}"
    
class IR_sete:
    def __init__(self, src, indent=0):
        self.src = src
        self.indent = indent
    def __repr__(self):
        return f"{INDENT * self.indent}sete {self.src}"

class IR_setne:
    def __init__(self, src, indent=0):
        self.src = src
        self.indent = indent
    def __repr__(self):
        return f"{INDENT * self.indent}setne {self.src}"

class IR_movzbl:
    def __init__(self, src, dest, indent=0):
        self.src = src
        self.dest = dest
        self.indent = indent
    def __repr__(self):
        return f"{INDENT * self.indent}movzbl {self.src}, {self.dest}"

class IR_je:
    def __init__(self, label, indent=0):
        self.label = label
        self.indent = indent
    def __repr__(self):
        return f"{INDENT * self.indent}je {self.label}"

class IR_jmp:
    def __init__(self, label, indent=0):
        self.label = label
        self.indent = indent
    def __repr__(self):
        return f"{INDENT * self.indent}jmp {self.label}"

class IR_label:
    def __init__(self, label, indent=0):
        self.label = label
        self.indent = indent
    def __repr__(self):
        return f"{INDENT * self.indent}{self.label}:"


class x86IR:

    def __init__(self, flat_tree):

        self.tree = flat_tree
        self.counter = 0
        self.IR_ = []
        self.generate_IR(self.tree, 0)

    def pop(self, i):
        self.IR_.pop(i)
    
    def insert(self, i, obj):
        self.IR_.insert(i, obj)

    def get_instruction_list(self):
        return self.IR_

    def __repr__(self):
        s = ""
        for instr in self.IR_:
            s += str(instr) + "\n"
        return s
        
    def generate_IR(self, node, indent):

        if isinstance(node, ast.Module):
            self.generate_IR(node.body, indent)
        
        elif isinstance(node, list):
            for child in node:
                self.generate_IR(child, indent)

        elif isinstance(node, ast.Assign):

            r_val = node.value
            l_val = node.targets[0].id

            if isinstance(r_val, ast.Expr):
                r_val = r_val.value

            if isinstance(r_val, ast.Call):

                if r_val.func.id == "eval":
                    self.IR_.append(IR_call("eval_input", l_val, indent))
                    return

                if r_val.func.id != "int":
                    
                    print(f"IR ERR : expecting an INT() but got {r_val.func.id}")
                    exit(0)

                if not isinstance(r_val.args[0], ast.Compare):

                    print(f"IR ERR : expecting an INT(Compare()) but got INT({r_val.args[0]}")
                    exit(0)
                
                left_cmp = to_str(r_val.args[0].left)
                right_cmp = to_str(r_val.args[0].comparators[0])

                if is_numeric(right_cmp): 

                    if is_numeric(left_cmp): # both are numbers
                        temp = "_temp"
                        self.IR_.append(IR_movl(right_cmp, temp, indent))
                        right_cmp = temp
                    
                    else:  # swap left and right (one of them is number)
                        temp = left_cmp
                        left_cmp = right_cmp
                        right_cmp = temp

                if isinstance(r_val.args[0].ops[0], ast.Eq):

                    self.IR_.append(IR_cmpl(left_cmp, right_cmp, indent))
                    self.IR_.append(IR_sete(f"%al", indent))
                    self.IR_.append(IR_movzbl(f"%al", l_val, indent))

                else:

                    self.IR_.append(IR_cmpl(left_cmp, right_cmp, indent))
                    self.IR_.append(IR_setne(f"%al", indent))
                    self.IR_.append(IR_movzbl(f"%al", l_val, indent))
                

            elif isinstance(r_val, ast.BinOp):

                left = to_str(r_val.left)
                right = to_str(r_val.right)

                # the following check
                # solves the issue of
                # v = t + v
                # translating to 
                # mov t, v
                # add v, v
                # (incorrect translation
                # due to invalid overwrite)
                # quick solution : swap operands

                if l_val == right:
                    temp = left
                    left = right
                    right = temp
                
                self.IR_.append(IR_movl(left, l_val, indent))
                self.IR_.append(IR_addl(right, l_val, indent))

            elif isinstance(r_val, ast.UnaryOp):

                op = to_str(r_val.operand)                    
                
                self.IR_.append(IR_movl(op, l_val, indent))
                self.IR_.append(IR_negl(l_val, indent))

            elif isinstance(r_val, ast.Constant):
                self.IR_.append(IR_movl(r_val.value, l_val, indent))
            
            elif isinstance(r_val, ast.Name):
                self.IR_.append(IR_movl(r_val.id, l_val, indent))
        
        elif isinstance(node, ast.Expr):

            if isinstance(node.value, ast.Call):
                if is_print(node.value.func.id):

                    arg_s = to_str(node.value.args[0])
                    self.IR_.append(IR_call("print", arg_s, indent))     
                
                elif is_eval_input(node.value.func.id):
                    self.IR_.append(IR_call("eval_input", "", indent))
        
        elif isinstance(node, ast.If):

            then_label = self.counter
            else_label = self.counter
            end_label = self.counter
            self.counter = self.counter + 1

            self.IR_.append(IR_cmpl("0", to_str(node.test), indent))
            self.IR_.append(IR_je(f"else{else_label}", indent))
            self.IR_.append(IR_label(f"then{then_label}", indent))

            self.generate_IR(node.body, indent + 1)

            self.IR_.append(IR_jmp(f"end{end_label}", indent + 1))
            self.IR_.append(IR_label(f"else{else_label}", indent))

            self.generate_IR(node.orelse, indent + 1)

            self.IR_.append(IR_label(f"end{end_label}", indent))

        elif isinstance(node, ast.While):

            while_label = self.counter
            self.counter = self.counter + 1

            self.IR_.append(IR_label(f"while{while_label}", indent))
            self.IR_.append(IR_cmpl("0", to_str(node.test), indent + 1))
            self.IR_.append(IR_je(f"end{while_label}", indent + 1))

            self.generate_IR(node.body, indent + 1)

            self.IR_.append(IR_jmp(f"while{while_label}", indent + 1))
            self.IR_.append(IR_label(f"end{while_label}", indent))
            
        else:
            print(f"Err: Unrecognized statement \'{node}\' in to_x86_IR()")
        
    
    def get_prog_vars(self):

        var_set = []
        lookup = set()

        for instr in self.IR_:

            if isinstance(instr, IR_movl) or isinstance(instr, IR_addl):
                if not is_numeric(instr.src):
                    add_to_list_unique(var_set, lookup, instr.src)
                add_to_list_unique(var_set, lookup, instr.dest)

            elif isinstance(instr, IR_movzbl):
                add_to_list_unique(var_set, lookup, instr.dest)

            elif isinstance(instr, IR_negl):
                add_to_list_unique(var_set, lookup, instr.src)

            elif isinstance(instr, IR_call):
                if not is_numeric(instr.args):
                    add_to_list_unique(var_set, lookup, instr.args)

        return var_set




def replace_instr_with_spill_code(IR, spill_code, idx):
    IR.pop(idx)
    i = 0
    while i < len(spill_code):
        IR.insert(idx + i, spill_code[i])
        i += 1 


def replace_double_stack_ref_with_spill_code(IR, double_stack_instrs):

    # this is sketchy

    ir_length_gain = 0
    temp_id = 0
    unspillable_vars = []
    IR_instrs = IR.get_instruction_list()

    for instr in double_stack_instrs:

        idx = instr.IR_index + ir_length_gain
        ir_instr = IR_instrs[idx]

        print(f"Replacing instruction {ir_instr} with spill code")

        if isinstance(ir_instr, IR_addl):

            addl = ir_instr

            spill_code = [IR_movl(addl.src, f"temp{temp_id}_UNSPILL", spill_code=True),
                          IR_movl(addl.dest, f"temp{temp_id + 1}_UNSPILL", spill_code=True),
                          IR_addl(f"temp{temp_id}_UNSPILL", f"temp{temp_id + 1}_UNSPILL", spill_code=True),
                          IR_movl(f"temp{temp_id + 1}_UNSPILL", addl.dest, spill_code=True)]

            unspillable_vars.append(f"temp{temp_id}_UNSPILL")
            unspillable_vars.append(f"temp{temp_id + 1}_UNSPILL")

            replace_instr_with_spill_code(IR, spill_code, idx)
            ir_length_gain += (len(spill_code) - 1)
            temp_id += 1

        elif isinstance(ir_instr, IR_movl):

            movl = ir_instr

            spill_code = [IR_movl(movl.src, f"temp{temp_id}_UNSPILL", spill_code=True),
                          IR_movl(f"temp{temp_id}_UNSPILL", movl.dest, spill_code=True)]
            
            unspillable_vars.append(f"temp{temp_id}_UNSPILL")

            replace_instr_with_spill_code(IR, spill_code, idx)
            ir_length_gain += (len(spill_code) - 1)
            temp_id += 1

        else:

            print(f"Err : Unrecognized instruction {ir_instr} in replace_double_stack_() ")

    return unspillable_vars