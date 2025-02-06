import sys
import os
from flatten import *
from unparser import *


if __name__ == "__main__":

    if (len(sys.argv) < 2):
        print("Usage: python3 <prog> <input python prog>")
        exit(1)
    
    py_file = sys.argv[1]
    
    if not os.path.exists(py_file):
        print(f"Could not open python file \'{py_file}\'")
        exit(1)
    
    with open(py_file, "r") as file:
        prog = file.read()

    
    tree = ast.parse(prog)
    renamed_tree = RenameVariables().visit(tree)
    flat_tree = flatten_ast(renamed_tree)
    flat_prog = UnParser().un_parse(flat_tree)

    print(f"======PROG=====")
    print(prog)

    print(f"====FLATTENED PROG======")
    print(flat_prog)
    
