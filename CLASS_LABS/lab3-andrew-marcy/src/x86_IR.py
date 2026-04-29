from unparser import *


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


class IR_movl:
    def __init__(self, src, dest, spill_code=False):
        self.src = str(src)
        self.dest = str(dest)
        self.spill_code = spill_code
    def __repr__(self):
        if self.spill_code:
            return f"\033[1mmovl {self.src}, {self.dest}\033[0m"
        else:
            return f"movl {self.src}, {self.dest}"

class IR_addl:
    def __init__(self, src, dest, spill_code=False):
        self.src = str(src)
        self.dest = str(dest)
        self.spill_code = spill_code
    def __repr__(self):
        if self.spill_code:
            return f"\033[1maddl {self.src}, {self.dest}\033[0m"
        else:
            return f"addl {self.src}, {self.dest}"

class IR_negl:
    def __init__(self, src, spill_code=False):
        self.src = str(src)
        self.spill_code = spill_code
    def __repr__(self):
        return f"negl {self.src}"

class IR_call:
    def __init__(self, id, args, spill_code=False):
        self.id = id
        self.args = args
        self.spill_code = spill_code
    def __repr__(self):
        if self.id == "eval_input":
            return f"eval_input {self.args}"
        if self.id == "print":
            return f"print {self.args}"


def get_prog_vars(IR):
    s = set()
    for instr in IR:
        if isinstance(instr, IR_movl) or isinstance(instr, IR_addl):
            if not is_numeric(instr.src):
                s |= {instr.src}
            s |= {instr.dest}
        if isinstance(instr, IR_negl):
            s |= {instr.src}
        if isinstance(instr, IR_call):
            if not is_numeric(instr.args):
                s |= {instr.args}
    return list(s)


def is_nop_movl(movl_op):
    return movl_op.src == movl_op.dest



class x86_IR_wrapper:
    def __init__(self, IR):
        self.IR = IR
    def __repr__(self):
        s = ""
        for instr in self.IR:
            s += str(instr) + "\n"
        return s



def replace_instr_with_spill_code(IR, spill_code, idx):
    IR.pop(idx)
    i = 0
    while i < len(spill_code):
        IR.insert(idx + i, spill_code[i])
        i += 1 


def replace_double_stack_ref_with_spill_code(IR, double_stack_instrs):

    # the trouble of traversing a mutating list
    # extremely sketchy but i was in a time crunch!
    ir_length_gain = 0
    temp_id = 0
    unspillable_vars = []

    for instr in double_stack_instrs:

        idx = instr.IR_index + ir_length_gain
        ir_instr = IR[idx]

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


def to_x86_IR(flat_tree):

    IR = []

    for child in flat_tree.body:

        if isinstance(child, ast.Assign):

            r_val = child.value
            l_val = child.targets[0].id

            if isinstance(r_val, ast.BinOp):

                left = to_str(r_val.left)
                right = to_str(r_val.right)

                ir_op_1 = IR_movl(src = left, dest = l_val)
                ir_op_2 = IR_addl(src = right, dest = l_val)

                # if not is_nop_movl(ir_op_1):
                
                IR.append(ir_op_1)
                IR.append(ir_op_2)

            elif isinstance(r_val, ast.UnaryOp):

                op = to_str(r_val.operand)

                ir_op_1 = IR_movl(src = op, dest = l_val)
                ir_op_2 = IR_negl(src = l_val)
                
                # if not is_nop_movl(ir_op_1):
                
                IR.append(ir_op_1)
                IR.append(ir_op_2)

            elif isinstance(r_val, ast.Constant):

                IR.append(IR_movl(src = r_val.value, dest = l_val))
            
            elif isinstance(r_val, ast.Name):

                ir_op_1 = IR_movl(src = r_val.id, dest = l_val)

                # if not is_nop_movl(ir_op_1):
                IR.append(ir_op_1)

            elif isinstance(r_val, ast.Call):

                if r_val.func.id == "eval":
                    IR.append(IR_call(id = "eval_input", args = l_val))
                else:
                    print(f"Err: Unrecognized function call \'{r_val.func.id}\'")
            
            else:
                print(f"Err: Unrecognized statement \'{r_val}\' in to_x86_IR()")
        
        elif isinstance(child, ast.Expr):

            if isinstance(child.value, ast.Call):

                if is_print(child.value.func.id):

                    arg_s = to_str(child.value.args[0])

                    IR.append(IR_call(id = "print", args = arg_s))     
                
                elif is_eval_input(child.value.func.id):

                    IR.append(IR_call(id = "eval_input", args = ""))

        else:
            print(f"Err: Unrecognized statement \'{child}\' in to_x86_IR()")

    return IR