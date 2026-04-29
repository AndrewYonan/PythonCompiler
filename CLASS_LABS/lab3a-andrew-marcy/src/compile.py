#!/usr/bin/env python3.10

import os
import sys
from ASTParser import *
from AST_to_pythonAST import *
from flatten import *
from unparser import *
from x86_IR import *
from liveness import *
from register_alloc import *
from python_to_x86 import *


def custom_parse(prog):
    lexer = Lexer(prog)
    parser = Parser(lexer)
    tree = parser.parse()
    converter = CustomToPythonASTConverter()
    py_ast_tree = converter.convert(tree)
    py_ast_tree = rename_source_variables(py_ast_tree)
    return py_ast_tree


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


def optimize_movls(instrList):
    opt_1 = remove_no_op_movls(instrList)
    opt_2 = remove_redundant_pair_movls(instrList)

    if (opt_1 > 0):
        print(f"[+] Removed {opt_1} NO-OP move instructions (a -> a)")
    if (opt_2 > 0):
        print(f"[+] Removed {opt_2} redundant swap move instructions (a -> b, b -> a)")


def compile_pipeline(prog):

    print("\n")
    sec("PYTHON3 PROG")
    print(prog)
    sec("")

    ITER = 0
    register_alloc_converged = False
    number_of_spilled_vars = 0
    unspillable_vars = []

    # AST = custom_parse(prog)
    AST = ast.parse(prog)

    AST = rename_source_variables(AST)
    flat_tree = flatten(AST)

    sec("FLAT PROG")
    print(un_parse(flat_tree), end="")
    sec("")

    IR = x86IR(flat_tree)   

    while not register_alloc_converged:

        compiler_LOG_header(ITER)

        sec("IR")
        print(IR)
        sec("")

        vars = IR.get_prog_vars()

        sec("Prog Vars")
        print(vars)
        sec("")

        BBL = BasicBlockList(IR)

        CFG = CFGraph(BBL)

        sec("CFG / Control-Flow")
        print(CFG)
        sec("")

        sec("CFG / Basic Blocks")
        print(BBL)
        sec("")

        LM = LivenessMap(CFG)

        sec("Liveness")
        print(LM)
        sec("")

        IG = UInterferenceGraph(vars, unspillable_vars, LM)

        sec("INTERFERENCE GRAPH + COLORS")
        print(IG, end="")
        sec("")

        RA = RegisterAllocation(IG)

        sec("HOMES ASSIGNED")
        print(RA, end="")
        sec("")

        spillage = RA.get_spillage()
        number_of_spilled_vars = len(spillage)

        sec("NUMBER OF SPILLED VARIABLES")
        print(number_of_spilled_vars)
        sec("")

        instrList = X86InstructionList(IR, RA)
        double_stack_instrs = instrList.get_double_stack_ref_instructions()

        sec("DOUBLE STACK REFS")
        print(double_stack_instrs)
        sec("")

        if len(double_stack_instrs) == 0:
            print("*****EXITING, No double stack references")
            register_alloc_converged = True
            break

        unspillable_vars = replace_double_stack_ref_with_spill_code(IR, double_stack_instrs)

        sec("UN-spillable vars")
        print(unspillable_vars)
        sec("")
        
        ITER += 1
    
    optimize_movls(instrList)

    x86_code = python_to_x86_asm(instrList)

    sec("GENERATED X86")
    print(x86_code, end="")
    sec("")

    print(f"FINISHED IN {ITER + 1} iterations")
 
    return x86_code




def compiler_LOG_header(idx):
    print("**************************************************************************")
    print(f"******************* NEW COMPILER PIPLINE ITERATION ({idx}) ***********************")
    print("**************************************************************************")


def sec(string):
    l = 25
    s = "=" * (l - len(string)//2)
    print(f"{s}{string}{s}")



if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage : python3 <prog> <python prog.py file to compile>")
        exit(1)

    src_py_file = sys.argv[1]

    if not os.path.exists(src_py_file):
        print(f"filename \'{src_py_file}\' could not be found") 
        exit(1)
    
    with open(src_py_file, 'r') as src_file:
        prog = src_file.read()

    x86_code = compile_pipeline(prog)

    dest_asm_file = src_py_file[:-2] + "s"

    with open(dest_asm_file, 'w') as dest_file:
        dest_file.write(x86_code)

