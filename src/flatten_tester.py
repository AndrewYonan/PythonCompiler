import ast
import subprocess
import os
import sys
from ast import *
from flatten import *
from unparser import *



def get_ast(prog):
    return ast.parse(prog)



def get_prog_output(file_name):
    try:
        process = subprocess.Popen(
            ["python3", file_name],  
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        stdout, stderr = process.communicate(input="66\n"*100) 

        return stdout.strip()

    except FileNotFoundError:
        return None, f"File '{file_name}' not found."
    except Exception as e:
        return None, str(e)



def test_case_prog(prog, i):
    
    tree = get_ast(prog)
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
        print(f"TEST CASE {i+1} Passed {check} ({output} = {output_flat})")
    else:
        print(f"TEST CASE {i+1} FAILED : PROG_OUTPUT : {output} | FLATTENED_PROG_OUTPUT : {output_flat}")
        print(f"prog : {prog}")



def test_all(test_dir_name):

    i = 0

    for file_name in os.listdir(test_dir_name):

        file_path = os.path.join(test_dir_name, file_name)

        if os.path.isfile(file_path):

            with open(file_path, "r") as test_case_file:

                prog = test_case_file.read()
                test_case_prog(prog, i)
            
            i = i + 1
        




if __name__ == "__main__":

    test_dir_name = "../tests/TEST_CASES"

    if not os.path.exists(test_dir_name):
        print(f"directory '{test_dir_name}' could not be opened")
        sys.exit(1)

    test_all(test_dir_name)

    subprocess.run("rm -r __pycache__", shell=True)
