import os
import sys
import subprocess
from ast import *
from flatten import *
from unparser import *

from ASTClasses import *
from ASTParser import *
from ASTParser import *
from ASTDump import *
from AST_to_pythonAST import CustomToPythonASTConverter

def get_prog_output(file_name):
    try:
        process = subprocess.Popen(
            ["python3", file_name],  
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        stdout, stderr = process.communicate(input="1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n") 

        return stdout.strip(), stderr.strip()

    except FileNotFoundError:
        return None, f"File '{file_name}' not found."
    except Exception as e:
        return None, str(e)


def custom_parse(prog):

    lexer = Lexer(prog)
    parser = Parser(lexer)
    tree = parser.parse()
    converter = CustomToPythonASTConverter()
    py_ast_tree = converter.convert(tree)
    py_ast_tree = rename_source_variables(py_ast_tree)

    return py_ast_tree

def test_case_prog(prog, i, file_path):
    
    # tree = custom_parse(prog)
    tree = ast.parse(prog)

    flat_tree = flatten(tree)
    prog_flat = un_parse(flat_tree)

    file_name = f"prog_file_{i}"
    file_name_flat = f"prog_file_{i}_FLAT"

    with open(file_name, "w") as file: 
        file.write(prog) 
    
    with open(file_name_flat, "w") as file_flat:
        file_flat.write(prog_flat)

    output, err_prog = get_prog_output(file_name)
    output_flat, err_flat_prog = get_prog_output(file_name_flat)

    os.remove(file_name)
    os.remove(file_name_flat)

    if err_prog != "":
        print(f"Prog \"{os.path.basename(file_path)}\" had error in it")
        return 0
    
    if err_flat_prog != "":
        print(f"Prog \"{os.path.basename(file_path)}\" FLAT program had ERROR : {err_flat_prog}")
        return 0

    if (output == output_flat):
        check = "\u2713"
        print(f"{os.path.basename(file_path)} --> TEST CASE {i+1} Passed {check} ({output.replace("\n", " ")} = {output_flat.replace("\n", " ")})")
        return 1
    else:
        print(f"{os.path.basename(file_path)} --> TEST CASE {i+1} FAILED : PROG_OUTPUT : {output.replace("\n", " ")} | FLATTENED_PROG_OUTPUT : {output_flat.replace("\n", " ")}")
        print(f"prog : {prog}")
        return 0



def test_all(test_dir_name):

    i = 0
    passed_sum = 0

    for file_name in os.listdir(test_dir_name):

        file_path = os.path.join(test_dir_name, file_name)

        if os.path.isfile(file_path):

            with open(file_path, "r") as test_case_file:

                prog = test_case_file.read()
                passed_sum += test_case_prog(prog, i, file_path)
            
            i = i + 1

    print(f"\n========= {passed_sum} / {i} TEST CASES PASSED ==========\n\n")


if __name__ == "__main__":

    if (len(sys.argv) < 2):
        print("Usage : python3 flatten_tester.py <directory containing python test programs>")
        exit(1)

    test_dir_name = sys.argv[1]

    if not os.path.exists(test_dir_name):
        print(f"directory '{test_dir_name}' could not be opened")
        sys.exit(1)

    test_all(test_dir_name)
