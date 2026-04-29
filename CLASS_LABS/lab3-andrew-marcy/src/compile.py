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


def remove_no_op_movls(instr_list):
    new_list = []
    for instr in instr_list.lst:
        if not (instr.type == "movl" and instr.src == instr.dest):
            new_list.append(instr)
    instr_list.lst = new_list


def remove_redundant_pair_movls(instr_list):
    new_list = []
    i = 0
    for instr in instr_list.lst:
        if i < len(instr_list.lst) - 1:
            this_op = instr
            next_op = instr_list.lst[i + 1]
            if contains_redundant_movl(this_op, next_op):
                instr_list.lst.pop(i + 1)
        i += 1


def compile_pipeline(prog):

    print("\n")
    sec("PYTHON3 PROG")
    print(prog)
    sec("")

    register_alloc_converged = False
    number_of_spilled_vars = 0
    unspillable_vars = []

    AST = custom_parse(prog)
    flat_tree = flatten(AST)

    sec("FLAT PROG")
    print(unparse(flat_tree), end="")
    sec("")

    IR = to_x86_IR(flat_tree)

    ITER = 0

    while not register_alloc_converged:

        compiler_debug_header(ITER)

        sec("IR")
        _IR = x86_IR_wrapper(IR)
        print(_IR, end="")
        sec("")

        LM = LivenessMap(IR)

        sec("LIVENESS SETS")
        print(LM, end="")
        sec("")

        # vars = get_local_vars(flat_tree)
        vars = get_prog_vars(IR)

        sec("LOCAL VARS")
        print(vars)
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

        sec("SPILLAGE")
        print(spillage)
        sec("")

        number_of_spilled_vars = len(spillage)

        sec("NUMBER OF SPILLED VARIABLES")
        print(number_of_spilled_vars)
        sec("")

        instrList = X86InstructionList(IR, RA)

        double_stack_instrs = instrList.get_double_stack_ref_instructions()

        if len(double_stack_instrs) == 0:
            print("*****EXITING, No double stack references")
            register_alloc_converged = True
            break

        unspillable_vars = replace_double_stack_ref_with_spill_code(IR, double_stack_instrs)

        sec("UN-spillable vars")
        print(unspillable_vars)
        sec("")

        ITER += 1

    remove_no_op_movls(instrList)
    remove_redundant_pair_movls(instrList)

    x86_code = python_to_x86_asm(instrList)

    sec("GENERATED X86")
    print(x86_code, end="")
    sec("")

    # print_pipeline_components(prog, flat_tree, IR, LM, IG, RA, x86_code)

    print(f"FINISHED IN {ITER + 1} iterations")
    
    return x86_code




def compiler_debug_header(idx):
    print("**************************************************************************")
    print(f"******************* NEW COMPILER PIPLINE ITERATION ({idx}) ***********************")
    print("**************************************************************************")


def sec(string):
    l = 25
    s = "=" * (l - len(string)//2)
    print(f"{s}{string}{s}")



def print_pipeline_components(prog, flat_tree, IR, LM, IG, RA, x86_code):

    print("\n")
    sec("PYTHON3 PROG")
    print(prog)
    sec("")

    sec("FLAT PROG")
    print(unparse(flat_tree), end="")
    sec("")

    sec("IR")
    _IR = x86_IR_wrapper(IR)
    print(_IR, end="")
    sec("")

    sec("LIVENESS SETS")
    print(LM, end="")
    sec("")

    sec("INTERFERENCE GRAPH")
    print(IG, end="")
    sec("")

    sec("HOMES ASSIGNED")
    print(RA, end="")
    sec("")

    sec("GENERATED X86")
    print(x86_code, end="")
    sec("")




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

