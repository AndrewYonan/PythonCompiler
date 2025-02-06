
import ast
import subprocess
import os
import sys
from ast import *
from flatten import *
from unparser import *

sys.path.append(os.path.abspath("Parsing"))
from Parsing import ASTClasses
from Parsing import ASTParser
from ASTParser import *
from Parsing import ASTDump
from Parsing import AST_to_pythonAST
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

        return stdout.strip()

    except FileNotFoundError:
        return None, f"File '{file_name}' not found."
    except Exception as e:
        return None, str(e)


def get_parse_tree(prog):

    lexer = Lexer(prog)

    parser = Parser(lexer)
    tree = parser.parse()

    converter = CustomToPythonASTConverter()
    py_ast_tree = converter.convert(tree)

    return py_ast_tree


def test_case_prog(prog, i, file_path):
    
    tree = get_parse_tree(prog)
    
    renamed_tree = RenameVariables().visit(tree)
    flat_tree = flatten_ast(renamed_tree)
    prog_flat = UnParser().un_parse(flat_tree)

    file_name = f"prog_file_{i}"
    file_name_flat = f"prog_file_{i}_FLAT"

    with open(file_name, "w") as file: 
        file.write(prog) 
    
    with open(file_name_flat, "w") as file_flat:
        file_flat.write(prog_flat)

    output = get_prog_output(file_name)
    output_flat = get_prog_output(file_name_flat)

    os.remove(file_name)
    os.remove(file_name_flat)

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

    test_dir_name = "../tests/TEST_CASES"

    if not os.path.exists(test_dir_name):
        print(f"directory '{test_dir_name}' could not be opened")
        sys.exit(1)

    test_all(test_dir_name)

    subprocess.run("rm -r __pycache__", shell=True)
