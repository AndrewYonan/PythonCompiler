from liveness import CFGraph
from x86_IR import *


def is_numeric(s):
    try:
        float(s) 
        return True
    except ValueError:
        return False


def get_key_with_value(dict, val):
    for key in dict:
        if dict[key] == val:
            return key

def get_negated_key_with_value(dict, val):
    for key in dict:
        if key[0] == "-":
            if dict[key] == val:
                return key[1:]
        

def replace_last_two_instrs_with_movl(idx, IR_instrs, new_movl):

    IR_instrs.pop(idx - 1)
    IR_instrs.pop(idx - 1)
    IR_instrs.insert(idx - 1, IRInstruction(new_movl))
    

def optimize_basic_block_LVN(block):

    value_table = {}
    opts = 0
    n = 1
    i = 0

    block_instrs = block.get_IR_instr_list()

    while i < len(block_instrs):

        instr = block_instrs[i].instruction

        if isinstance(instr, IR_movl):
            
            if instr.src in value_table:
                instr.src_n = value_table[instr.src]
                value_table[instr.dest] = value_table[instr.src]
                instr.dest_n = value_table[instr.src]
            
            else:

                value_table[instr.src] = n
                value_table[instr.dest] = n
                instr.src_n = n
                instr.dest_n = n
                n += 1
            
        
        elif isinstance(instr, IR_addl):


            if instr.src in value_table:
                instr.src_n = value_table[instr.src]

            else:
                value_table[instr.src] = n
                instr.src_n = n
                n += 1
                
            
            if instr.dest not in value_table:
                print(f"ERR : in LVN, instr {instr} doesn't have a known dest \"{instr.dest}\"")
                exit(1)

            expr = f"{value_table[instr.src]} + {value_table[instr.dest]}"

            if expr in value_table:

                existing_var_for_expr = get_key_with_value(value_table, value_table[expr])
                
                new_movl_instr = IR_movl(existing_var_for_expr, instr.dest)
                new_movl_instr.src_n = value_table[expr]
                new_movl_instr.dest_n = value_table[expr]

                replace_last_two_instrs_with_movl(i, block_instrs, new_movl_instr)
                opts += 1
                i -= 1

                instr.dest_n = value_table[expr]
                value_table[instr.dest] = value_table[expr]

            else:
                value_table[expr] = n
                value_table[instr.dest] = n
                instr.dest_n = n
                n += 1
        
        elif isinstance(instr, IR_negl):
            
            if instr.src not in value_table:
                print(f"ERR : in LVN, instr {instr} doesn't have a known src \"{instr.src}\"")
                exit(1)

            expr = f"-{value_table[instr.src]}"

            if expr in value_table:

                existing_var_for_expr = get_key_with_value(value_table, value_table[expr])
                
                new_movl_instr = IR_movl(existing_var_for_expr, instr.src)
                new_movl_instr.src_n = value_table[expr]
                new_movl_instr.dest_n = value_table[expr]

                block_instrs[i] = IRInstruction(new_movl_instr)
                opts += 1

                instr.src_n = value_table[expr]
                value_table[instr.src_n] = value_table[expr]

            else:
                value_table[expr] = n
                value_table[instr.src] = n
                instr.src_n = n
                n += 1

        i += 1
    
    # print(f"===>>>> VALUE_TABLE = {value_table}")
    return opts


def optimize_constant_fold_block(block):

    constant_table = {}
    opts = 0

    block_instrs = block.get_IR_instr_list()

    for i in range(len(block_instrs)):

        instr = block_instrs[i].instruction

        if isinstance(instr, IR_movl):
            if is_numeric(instr.src):

                constant_table[instr.dest] = instr.src
            
            elif instr.src in constant_table:

                constant_table[instr.dest] = constant_table[instr.src]


        elif isinstance(instr, IR_addl):

            src_numeric = is_numeric(instr.src)
            src_in_const_table = instr.src in constant_table
            dest_in_const_table = instr.dest in constant_table

            if src_in_const_table:
                if constant_table[instr.src] == "UNKNOWN":
                    constant_table[instr.dest] = "UNKNOWN"
                    continue
            
            if dest_in_const_table:
                if constant_table[instr.dest] == "UNKNOWN":
                    continue

            if (src_numeric or src_in_const_table):
            
                src_const = int(instr.src) if src_numeric else int(constant_table[instr.src])

                if instr.dest in constant_table:
                    
                    dest_const = int(constant_table[instr.dest])

                    fold_val = src_const + dest_const

                    new_movl_instr = IR_movl(f"{fold_val}", instr.dest)
                    constant_table[instr.dest] = str(fold_val)

                    block_instrs[i] = IRInstruction(new_movl_instr)
                    opts += 1


        elif isinstance(instr, IR_negl):

            if instr.src in constant_table:

                if constant_table[instr.src] == "UNKNOWN":
                    continue
                
                fold_val = -int(constant_table[instr.src])

                new_movl_instr = IR_movl(f"{fold_val}", instr.src)
                constant_table[instr.src] = str(fold_val)

                block_instrs[i] = IRInstruction(new_movl_instr)
                opts += 1

        elif isinstance(instr, IR_call):

            if instr.id == "eval_input":

                store_var = instr.args

                constant_table[store_var] = "UNKNOWN"
    
    # print(f"CONSTANT TABLE : {constant_table}")
    return opts


# DO NOT USE (unfinished)
def optimize_copy_fold_block(block):

    value_table = {}
    opts = 0
    n = 1
    i = 0

    block_instrs = block.get_IR_instr_list()

    while i < len(block_instrs):

        instr = block_instrs[i].instruction

        if isinstance(instr, IR_movl):
            
            if instr.src in value_table:
                instr.src_n = value_table[instr.src]
                value_table[instr.dest] = value_table[instr.src]
                instr.dest_n = value_table[instr.src]
            
            else:

                value_table[instr.src] = n
                value_table[instr.dest] = n
                instr.src_n = n
                instr.dest_n = n
                n += 1
            
        elif isinstance(instr, IR_addl):


            if instr.src in value_table:
                instr.src_n = value_table[instr.src]

            else:
                value_table[instr.src] = n
                instr.src_n = n
                n += 1
                
            
            if instr.dest not in value_table:
                print(f"ERR : in LVN, instr {instr} doesn't have a known dest \"{instr.dest}\"")
                exit(1)

            expr = f"{value_table[instr.src]} + {value_table[instr.dest]}"

            if expr in value_table:

                existing_var_for_expr = get_key_with_value(value_table, value_table[expr])
                
                new_movl_instr = IR_movl(existing_var_for_expr, instr.dest)
                new_movl_instr.src_n = value_table[expr]
                new_movl_instr.dest_n = value_table[expr]

                replace_last_two_instrs_with_movl(i, block_instrs, new_movl_instr)
                opts += 1
                i -= 1

                instr.dest_n = value_table[expr]
                value_table[instr.dest] = value_table[expr]

            else:
                value_table[expr] = n
                value_table[instr.dest] = n
                instr.dest_n = n
                n += 1
        
        elif isinstance(instr, IR_negl):
            
            if instr.src not in value_table:
                print(f"ERR : in copy-fold, instr {instr} doesn't have a known src \"{instr.src}\"")
                exit(1)

            operand = value_table[instr.src]
            expr = f"-{operand}"

            # print(f"\n\n<<==>> New value search in copy-fold()")
            # print(f"looking for keys whose value is {operand}")
            # print(f"operand = {operand}")
            # print(f"expr = {expr}")
            # print(f"TB = {value_table}")
            
            value_whose_negation_is_operand = get_negated_key_with_value(value_table, operand)

            # print(f"value_whose_negation_is_operand = {value_whose_negation_is_operand}")

            if value_whose_negation_is_operand:

                existing_var_for_expr = get_key_with_value(value_table, int(value_whose_negation_is_operand))
                # print(f"existing var for expr = {existing_var_for_expr}")

                new_movl_instr = IR_movl(existing_var_for_expr, instr.src)
                new_movl_instr.src_n = value_table[existing_var_for_expr]
                new_movl_instr.dest_n = value_table[existing_var_for_expr]
                
                block_instrs[i] = IRInstruction(new_movl_instr)
                opts += 1

                instr.src_n = value_table[existing_var_for_expr]
                value_table[str(instr.src_n)] = value_table[existing_var_for_expr] 

            else:
                value_table[expr] = n
                value_table[instr.src] = n
                instr.src_n = n
                n += 1

        i += 1
    
    # print(f"===>>>> VALUE_TABLE = {value_table}")
    return opts




def optimize_constant_fold(basic_block_list):
    opts = 0
    for block in basic_block_list.get_basic_blocks():
        opts += optimize_constant_fold_block(block)
    return opts

def optimize_copy_fold(basic_block_list):
    opts = 0
    for block in basic_block_list.get_basic_blocks():
        opts += optimize_copy_fold_block(block)
    return opts


def optimize_LVN(basic_block_list):
    opts = 0
    for block in basic_block_list.get_basic_blocks():
        opts += optimize_basic_block_LVN(block)
    return opts


def optimize_dead_store_basic_block(block):

    opts = 0
    i = 0
    block_instrs = block.get_IR_instr_list()

    while i < len(block_instrs):

        instr = block_instrs[i].instruction

        if isinstance(instr, IR_movl):

            liveness_set_after = block.get_instr_liveness_after(i)

            if instr.dest not in liveness_set_after:
                # print(f"Removing dead-store operation {block_instrs[i].instruction} because target {instr.dest} is not in liveness after = {liveness_set_after}")
                block_instrs.pop(i)
                i -= 1
                opts += 1
        
        elif isinstance(instr, IR_negl):

            liveness_set_after = block.get_instr_liveness_after(i)

            if instr.src not in liveness_set_after:
                # print(f"Removing dead-store operation {block_instrs[i].instruction} because target {instr.dest} is not in liveness after = {liveness_set_after}")
                block_instrs.pop(i)
                i -= 1
                opts += 1

        i += 1

    return opts




def remove_dead_stores(basic_block_list):

    opts = 0

    for block in basic_block_list.get_basic_blocks():
        opts += optimize_dead_store_basic_block(block)
            
    return opts



def optimize_dead_stores(basic_block_list):

    opts = 0
    iters = 0

    while 1:

        iters += 1
        dead_stores_removed = remove_dead_stores(basic_block_list)

        if dead_stores_removed == 0:
            break

        opts += dead_stores_removed
    
    return opts
    

def contains_redundant_movl(op_1, op_2):
    if op_1.type == "movl" and op_2.type == "movl":
        if op_1.src == op_2.dest and op_1.dest == op_2.src:
            return True
    return False


def is_no_op_movl(instr):
    if instr.type == "movl" and (instr.src == instr.dest):
        return True
    return False


def remove_no_op_movls(instr_list):
    new_list = []
    counter = 0
    for instr in instr_list.lst:
        if not (is_no_op_movl(instr)):
            new_list.append(instr)
        else:
            counter += 1
    instr_list.lst = new_list
    return counter


def remove_redundant_pair_movls(instr_list):
    i = 0
    counter = 0
    for instr in instr_list.lst:
        if i < len(instr_list.lst) - 1:
            this_op = instr
            next_op = instr_list.lst[i + 1]
            if contains_redundant_movl(this_op, next_op):
                instr_list.lst.pop(i + 1)
                counter += 1
        i += 1
    return counter


def remove_trivial_moves(instrList):
    return remove_no_op_movls(instrList)

def remove_trivial_swap_moves(instrList):
    return remove_redundant_pair_movls(instrList)    

        

