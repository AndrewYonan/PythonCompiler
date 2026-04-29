#!/usr/bin/env python3.10

import os
import sys
import ast
from ast import *
from python_to_x86 import *

        

def compile(src_py_file):

    dest_asm_file = src_py_file[:-2] + "s"

    with open(src_py_file, 'r') as src_file:
        py_prog = src_file.read()

    asm_prog = python_to_x86_asm(py_prog)

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
            

            







