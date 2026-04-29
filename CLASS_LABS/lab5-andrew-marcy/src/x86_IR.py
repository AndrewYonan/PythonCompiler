from unparser import *

INDENT = "    "
SHOW_LVN_FLAG = False
SHOW_DEAD_STORE_FLAG = False
SHOW_LIVENESS = True

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
    
def is_var(s):
    return not is_numeric(s)

def to_str(atomic):
    if isinstance(atomic, ast.Name):
        return atomic.id
    if isinstance(atomic, ast.Constant):
        return str(atomic.value)

def to_str_args(ast_args):
    return list(map(lambda arg : to_str(arg), ast_args))

def arg_format(arg_strings):
    ret_str = ""
    for i in range(len(arg_strings)):
        ret_str += arg_strings[i]
        if i < len(arg_strings) - 1:
            ret_str += ", "
    return ret_str

def add_to_list_unique(lst, look_up_set, elem):
    if elem not in look_up_set:
        lst.append(elem)
        look_up_set.add(elem)


class IRInstruction:
    def __init__(self, instruction):
        self.instruction = instruction
        self.liveness_before = set()
        self.LOG_offset = 50
    def __repr__(self):
        s1 = str(self.instruction)
        s2 = str(sorted(list(self.liveness_before)))
        space = max(self.LOG_offset - len(s1), 0)
        space_s = "-" * space
        if SHOW_LIVENESS:
            #{s1}{space_s}
            return f"LBefore = \033[1m{s2}\033[0m"
        else:
            return f"{s1}"


#src_n and dest_n ints for LVN optimization

class IR_movl:
    def __init__(self, src, dest, indent=0, spill_code=False):
        self.src = str(src)
        self.dest = str(dest)
        self.src_n = 0
        self.dest_n = 0
        self.spill_code = spill_code
        self.indent = indent
        self.dead_store_marker = False
    def __repr__(self):
        if self.spill_code:
            return f"{INDENT * self.indent}\033[1mmovl {self.src}, {self.dest}\033[0m <--- SPILL"
        elif SHOW_LVN_FLAG:
            return f"{INDENT * self.indent}movl {self.src}(\033[1m{self.src_n}\033[0m), {self.dest}(\033[1m{self.dest_n}\033[0m)"
        elif self.dead_store_marker:
            return f"{INDENT * self.indent}movl {self.src}, {self.dest} <--------------- DEAD STORE"
        else:
            return f"{INDENT * self.indent}movl {self.src}, {self.dest}"
        
class IR_movzbl:
    def __init__(self, src, dest, indent=0, spill_code=False):
        self.src = src
        self.dest = dest
        self.indent = indent
        self.spill_code = spill_code
    def __repr__(self):
        if self.spill_code:
            return f"{INDENT * self.indent}\033[1mmovzbl {self.src}, {self.dest}\033[0m <--- SPILL"
        else:
            return f"{INDENT * self.indent}movzbl {self.src}, {self.dest}"


class IR_addl:
    def __init__(self, src, dest, indent=0, spill_code=False):
        self.src = str(src)
        self.dest = str(dest)
        self.src_n = 0
        self.dest_n = 0
        self.spill_code = spill_code
        self.indent = indent
    def __repr__(self):
        if self.spill_code:
            return f"{INDENT * self.indent}\033[1maddl {self.src}, {self.dest}\033[0m"
        elif SHOW_LVN_FLAG:
            return f"{INDENT * self.indent}addl {self.src}(\033[1m{self.src_n}\033[0m), {self.dest}(\033[1m{self.dest_n}\033[0m)"
        else:
            return f"{INDENT * self.indent}addl {self.src}, {self.dest}"

class IR_cmpl:
    def __init__(self, src, dest, indent=0, spill_code=False):
        self.src = src
        self.dest = dest
        self.indent = indent
        self.spill_code = spill_code
    def __repr__(self):
        if self.spill_code:
            return f"{INDENT * self.indent}\033[1mcmpl {self.src}, {self.dest}\033[0m <--- SPILL"
        else:
            return f"{INDENT * self.indent}cmpl {self.src}, {self.dest}"

class IR_negl:
    def __init__(self, src, indent=0):
        self.src = str(src)
        self.indent = indent
        self.src_n = 0
    def __repr__(self):
        if SHOW_LVN_FLAG:
            return f"{INDENT * self.indent}negl {self.src}(\033[1m{self.src_n}\033[0m)"
        else:
            return f"{INDENT * self.indent}negl {self.src}"

class IR_call:
    def __init__(self, id, args, target, indent=0):
        self.id = id
        self.args = args
        self.target = target
        self.indent = indent
    def __repr__(self):
        if self.target == None:
            t = ""
        else:
            t = self.target
        return f"{INDENT * self.indent}{self.id}({arg_format(self.args)}) {t}"
    
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


def is_primitive_type_transform(fn):
    if fn == "inject_bool":
        return 1
    elif fn == "inject_int":
        return 1
    elif fn == "project_bool":
        return 1
    elif fn == "project_int":
        return 1
    elif fn == "is_bool":
        return 1
    elif fn == "is_int":
        return 1
    elif fn == "is_true":
        return 1
    else:
        return 0


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
        i = 0
        for instr in self.IR_:
            s += str(i) + ": " + str(instr) + "\n"
            i += 1
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

                id = r_val.func.id
                target = l_val
                args = to_str_args(r_val.args)
                
                self.IR_.append(IR_call(id, args, target, indent))
            
            elif isinstance(r_val, ast.Compare):
                
                left_cmp = to_str(r_val.left)
                right_cmp = to_str(r_val.comparators[0])

                if is_numeric(right_cmp): 

                    if is_numeric(left_cmp): # both are numbers
                        temp = "_temp"
                        self.IR_.append(IR_movl(right_cmp, temp, indent))
                        right_cmp = temp
                    
                    else:  # swap left and right (one of them is number)
                        temp = left_cmp
                        left_cmp = right_cmp
                        right_cmp = temp

                if isinstance(r_val.ops[0], ast.Eq):

                    self.IR_.append(IR_cmpl(left_cmp, right_cmp, indent))
                    self.IR_.append(IR_sete(f"%al", indent))
                    self.IR_.append(IR_movzbl(f"%al", l_val, indent))

                elif isinstance(r_val.ops[0], ast.NotEq):

                    self.IR_.append(IR_cmpl(left_cmp, right_cmp, indent))
                    self.IR_.append(IR_setne(f"%al", indent))
                    self.IR_.append(IR_movzbl(f"%al", l_val, indent))

                else:

                    print(f"x86IR Err : unrecognized operator {r_val.ops[0]} for compare()")
                    exit(1)

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

            # refactor into combined expression:

            if isinstance(node.value, ast.Call):

                id = node.value.func.id
                args = to_str_args(node.value.args)

                if is_print(id):
                    self.IR_.append(IR_call("print_any", args, None, indent))     
                
                elif is_eval_input(id):
                    self.IR_.append(IR_call("eval_input_pyobj", [], None, indent))
                
                else:
                    self.IR_.append(IR_call(id, args, None, indent))
        
        elif isinstance(node, ast.If):

            then_label = self.counter
            else_label = self.counter
            end_label = self.counter
            self.counter += 1

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
            self.counter += 1

            self.IR_.append(IR_label(f"while{while_label}", indent))
            self.IR_.append(IR_cmpl("0", to_str(node.test), indent + 1))
            self.IR_.append(IR_je(f"end{while_label}", indent + 1))

            self.generate_IR(node.body, indent + 1)

            self.IR_.append(IR_jmp(f"while{while_label}", indent + 1))
            self.IR_.append(IR_label(f"end{while_label}", indent))
            
        else:
            print(f"Err: Unrecognized statement \'{node}\' in to_x86_IR()")
    
    
    # NOTE_: cmpl will never operated on Un-defined variables
    # NOTE_: negls will never operated on Un-defined variables

    def get_prog_vars(self):

        var_set = []
        lookup = set()

        for instr in self.IR_:

            if isinstance(instr, IR_movl) or isinstance(instr, IR_addl):
                if is_var(instr.src):
                    add_to_list_unique(var_set, lookup, instr.src)
                if is_var(instr.dest):
                    add_to_list_unique(var_set, lookup, instr.dest)

            elif isinstance(instr, IR_movzbl):
                if is_var(instr.dest):
                    add_to_list_unique(var_set, lookup, instr.dest)

            elif isinstance(instr, IR_call):
                if instr.target != None:
                    add_to_list_unique(var_set, lookup, instr.target)

        return var_set


    def take_updated_instructions_from_basic_blocks(self, basic_block_list):
        self.IR_ = []
        for block in basic_block_list.get_basic_blocks():
            for IR_instr in block.get_IR_instr_list():
                self.IR_.append(IR_instr.instruction)

    def take_instructions_from_liveness_map(self, liveness_map):
        self.IR_ = []
        i = 0
        IR_instrs = liveness_map.IR_instr_list
        while i < len(IR_instrs):
            instr = IR_instrs[i].instruction
            self.IR_.append(instr)
            i += 1


def x86_to_ir(x86_instr, RA):

    if x86_instr.type == "movl":

        src = RA.get_var(x86_instr.src)  
        dest = RA.get_var(x86_instr.dest)
        return IR_movl(src, dest)

    elif x86_instr.type == "addl":

        src = RA.get_var(x86_instr.src)  
        dest = RA.get_var(x86_instr.dest)
        return IR_addl(src, dest)

    elif x86_instr.type == "movzbl":

        dest = RA.get_var(x86_instr.dest)
        return IR_movzbl(f"%al", dest)

    elif x86_instr.type == "cmpl":

        src = RA.get_var(x86_instr.src)  
        dest = RA.get_var(x86_instr.dest)
        return IR_cmpl(src, dest)

    else:
        print("Err Pinocheo")
        exit(1)

    print("Err Rudolf the rednosed reindeer")
    exit(1)
    return 


def replace_instr_with_spill_code(IR, spill_code, idx):
    IR.pop(idx)
    i = 0
    while i < len(spill_code):
        IR.insert(idx + i, spill_code[i])
        i += 1 


def equal(ir_instr_1, ir_instr_2):
    if type(ir_instr_1) is type(ir_instr_2):
        return ((ir_instr_1.src == ir_instr_2.src) 
              & (ir_instr_1.dest == ir_instr_2.dest))
    return False


def replace_IR_instrs_with_spill_code(ir_instr_to_replace, IR):

    temp_id = 0
    unspillable_vars = set()
    IR_instrs = IR.get_instruction_list()

    for i in range(len(IR_instrs)):

        ir_instr = IR_instrs[i]

        if equal(ir_instr, ir_instr_to_replace):

            if isinstance(ir_instr, IR_addl):

                addl = ir_instr
                tmp1 = f"temp{temp_id}_UNSPILL"
                tmp2 = f"temp{temp_id + 1}_UNSPILL"

                spill_code = [IR_movl(addl.src, tmp1, spill_code=True),
                              IR_movl(addl.dest, tmp2, spill_code=True),
                              IR_addl(tmp1, tmp2, spill_code=True),
                              IR_movl(tmp2, addl.dest, spill_code=True)]

                unspillable_vars.add(tmp1)
                unspillable_vars.add(tmp2)

                replace_instr_with_spill_code(IR, spill_code, i)
                temp_id += 2

            elif isinstance(ir_instr, IR_movl):

                movl = ir_instr
                tmp1 = f"temp{temp_id}_UNSPILL"

                spill_code = [IR_movl(movl.src, tmp1, spill_code=True),
                              IR_movl(tmp1, movl.dest, spill_code=True)]
                
                unspillable_vars.add(tmp1)

                replace_instr_with_spill_code(IR, spill_code, i)
                temp_id += 1
            
            elif isinstance(ir_instr, IR_movzbl):
                
                movzbl = ir_instr
                tmp1 = f"temp{temp_id}_UNSPILL"
                
                spill_code = [IR_movzbl(movzbl.src, tmp1, spill_code=True),
                              IR_movl(tmp1, movzbl.dest, spill_code=True)]
                
                unspillable_vars.add(tmp1)
                
                replace_instr_with_spill_code(IR, spill_code, i)
                temp_id += 1

            elif isinstance(ir_instr, IR_cmpl):

                cmpl = ir_instr
                tmp1 = f"temp{temp_id}_UNSPILL"
                tmp2 = f"temp{temp_id + 1}_UNSPILL"

                spill_code = [IR_movl(cmpl.src, tmp1, spill_code=True),
                              IR_movl(cmpl.dest, tmp2, spill_code=True),
                              IR_cmpl(tmp1, tmp2, spill_code=True)]

                unspillable_vars.add(tmp1)
                unspillable_vars.add(tmp2)

                replace_instr_with_spill_code(IR, spill_code, i)
                temp_id += 2

            else:

                print(f"Err : Unrecognized instruction {ir_instr} in replace_bad_instrs_() ")
                exit(1)

    return unspillable_vars


def replace_instructions_with_spill_code(IR, RA, spill_replace_instrs):

    unspillable_vars = set()
    for instr_to_replace in spill_replace_instrs:

        ir_instr_to_replace = x86_to_ir(instr_to_replace, RA)
        print(f"Replacing the following IR instruction : {ir_instr_to_replace} : {instr_to_replace}")

        unspillable_vars |= replace_IR_instrs_with_spill_code(ir_instr_to_replace, IR)

    return unspillable_vars

