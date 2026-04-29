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
from optimization import *

def custom_parse(prog):
    lexer = Lexer(prog)
    parser = Parser(lexer)
    tree = parser.parse()
    converter = CustomToPythonASTConverter()
    py_ast_tree = converter.convert(tree)
    py_ast_tree = rename_source_variables(py_ast_tree)
    return py_ast_tree


def compile_pipeline(prog):
    
    optimizations = []
    LVN_opts = 0
    dead_store_opts = 0
    const_fold_opts = 0
    copy_fold_opts = 0
    trival_move_opts = 0
    trivial_swap_move_opts = 0
    MAX_ITERS = 10
    ITERS = 0
    
    optimizations.append('dead-store')
    optimizations.append('trivial-move')
    optimizations.append('trivial-swap-move')
    optimizations.append('LVN')
    optimizations.append('const-fold')

    print("\n")
    sec("PYTHON3 PROG")
    print(prog)
    sec("")

    unspillable_vars = []

    # AST = custom_parse(prog)
    AST = ast.parse(prog)

    AST = rename_source_variables(AST)
    flat_tree = flatten(AST)

    sec("FLAT PROG")
    print(un_parse(flat_tree), end="")
    sec("")

    IR = x86IR(flat_tree)   

    while 1:

        compiler_LOG_header(ITERS)

        sec("IR")
        print(IR)
        sec("")

        vars = IR.get_prog_vars()

        sec("Prog Vars")
        print(vars)
        sec("")

        BBL = BasicBlockList(IR)

        LVN_opts += (optimize_LVN(BBL) if 'LVN' in optimizations else 0)  
        copy_fold_opts += (optimize_copy_fold(BBL) if 'copy-fold' in optimizations else 0)
        const_fold_opts += (optimize_constant_fold(BBL) if 'const-fold' in optimizations else 0)
        IR.take_updated_instructions_from_basic_blocks(BBL)

        # sec("BBL - after constant folding")
        # print(BBL)
        # sec("")

        # sec("LVN-optimized IR")
        # print(IR)
        # sec("")

        CFG = CFGraph(BBL)

        # sec("CFG / Control-Flow")
        # print(CFG)
        # sec("")

        LM = LivenessMap(CFG)

        sec("BEFORE dead-store elim")
        print(BBL)
        sec("")

        dead_store_opts += (optimize_dead_stores(BBL) if 'dead-store' in optimizations else 0)
        IR.take_updated_instructions_from_basic_blocks(BBL)
        
        # sec("AFTER dead-store elim")
        # print(BBL)
        # sec("")

        IG = UInterferenceGraph(vars, unspillable_vars, LM)

        # sec("INTERFERENCE GRAPH + COLORS")
        # print(IG, end="")
        # sec("")

        RA = RegisterAllocation(IG)

        sec("HOMES ASSIGNED")
        print(RA, end="")
        sec("")

        spillage = RA.get_spillage()
        number_of_spilled_vars = len(spillage)

        # sec("NUMBER OF SPILLED VARIABLES")
        # print(number_of_spilled_vars)
        # sec("")

        # print(f"Getting instru_list from IR : <<<<---->>>>>")
        # print(IR)

        instrList = X86InstructionList(IR, RA)
        spill_required_instrs = instrList.get_spill_required_instructions()

        if len(spill_required_instrs) == 0:
            print("\n*****EXITING, No Spill-required instructions (2-address stack refs, movzbl stack refs)\n")
            break

        unspillable_vars = replace_instructions_with_spill_code(IR, spill_required_instrs)

        sec("UN-spillable vars")
        print(unspillable_vars)
        sec("")
        
        ITERS += 1
        
        if ITERS >= MAX_ITERS:
            print(f"COMPILER ERR : took too many iterations to converge")
            exit(1)
    
    trival_move_opts += (remove_trivial_moves(instrList) if 'trivial-move' in optimizations else 0)
    trivial_swap_move_opts += (remove_trivial_swap_moves(instrList) if 'trivial-swap-move' in optimizations else 0)

    x86_code = python_to_x86_asm(instrList)
    code_len = x86_code.count('\n')
    
    sec("GENERATED X86")
    print(x86_code, end="")
    sec("")

    print(f"ON optimizaitons : {optimizations}")
    print(f"[+] removed {dead_store_opts} dead-store operations")
    print(f"[+] LVN-optimization removed {LVN_opts} redundant computations")
    print(f"[+] Constant folding removed {const_fold_opts} computations")
    print(f"[+] Copy folding removed {copy_fold_opts} computations")
    print(f"[+] Removed {trival_move_opts} trivial move instructions (a -> a)")
    print(f"[+] Removed {trivial_swap_move_opts} trivial swap-move instructions (a -> b, b -> a)")
    print(f"x86 code length (lines) : {code_len}")
    print(f"FINISHED IN {ITERS} iterations")
 
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

