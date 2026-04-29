#!/usr/bin/env python3.10

import os
import sys
import ast
from ast import *
from python_to_x86 import *
from ASTParser import *
from AST_to_pythonAST import *



def custom_parse(prog):

    lexer = Lexer(prog)
    parser = Parser(lexer)
    tree = parser.parse()
    converter = CustomToPythonASTConverter()
    py_ast_tree = converter.convert(tree)

    return py_ast_tree

     

def compile(src_py_file):

    dest_asm_file = src_py_file[:-2] + "s"

    with open(src_py_file, 'r') as src_file:
        py_prog = src_file.read()

    # py_prog_AST = ast.parse(py_prog)
    py_prog_AST = custom_parse(py_prog)

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

    asm_prog = python_to_x86_asm(py_prog_AST_FLAT)

    with open(dest_asm_file, 'w') as dest_file:
        dest_file.write(asm_prog)
    

        

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage : python3 <prog> <python prog.py file to compile>")
        exit(1)

    filename = sys.argv[1]

    if not os.path.exists(filename):
        print(f"filename \'{filename}\' could not be found") 
        exit(1)

    compile(filename)
            

            







