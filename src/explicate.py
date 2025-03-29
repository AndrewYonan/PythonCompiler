import ast
from ast import *
from flatten import *
from unparser import *


def is_numeric(s):
    try:
        float(s) 
        return True
    except ValueError:
        return False

def to_atomic_str(node):
    if isinstance(node, ast.Constant):
        return str(node.value)
    elif isinstance(node, ast.Name):
        return node.id
    else:
        print(f"ERR : to_atomic_str({node})")
        exit(1)


def to_op_str(node):
    if isinstance(node, ast.Eq):
        return "=="
    elif isinstance(node, ast.NotEq):
        return "!="
    elif isinstance(node, ast.Is):
        return "is"
    else:
        print(f"ERR : to_op_str({node})")
        exit(1)


def to_int_literal(str):
    if is_explicit_FALSE(str):
        return 0
    elif is_explicit_TRUE(str):
        return 1
    else:
        return int(str)


def is_explicit_TRUE(str):
    return str == "True"

def is_explicit_FALSE(str):
    return str == "False"

def is_explicit_INT(str):
    return is_numeric(str)

def is_explicit_BOOL(str):
    return is_explicit_FALSE(str) or is_explicit_TRUE(str)

def is_explicit_int_or_bool(str):
    return is_explicit_BOOL(str) or is_explicit_INT(str)

#===================================================================
# EXPLICATION

def assign_eval_input_explicate_code(target):
    return f"""{target} = eval_input_pyobj()"""

def call_print_explicate_code(arg):
    return f"""print_any({arg})"""

def assign_atomic_explicate_code(target, right):

    exp_code = f""""""
    if is_explicit_INT(right):
        r_val = to_int_literal(right)
        exp_code += f"""{target} = inject_int({r_val})\n"""
    elif is_explicit_BOOL(right):
        r_val = to_int_literal(right)
        exp_code += f"""{target} = inject_bool({r_val})\n"""
    else:
        exp_code += f"""{target} = inject_bool({right})\n"""

    return exp_code


def compare_explicate_code(target, left, op, right, tmp1, tmp2):

    exp_code = f""""""
    if is_explicit_int_or_bool(left):
        l_val = to_int_literal(left)
        exp_code += f"""{tmp1} = inject_int({l_val})\n"""
    else:
        exp_code += f"""{tmp1} = {left}\n"""
    if is_explicit_int_or_bool(right):
        r_val = to_int_literal(right)
        exp_code += f"""{tmp2} = inject_int({r_val})\n"""
    else:
        exp_code += f"""{tmp2} = {right}\n"""

    if op == "is":
        exp_code += f"""
if is_int({tmp1}):
    if is_int({tmp2}):
        if project_int({tmp1}) == project_int({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
    elif is_bool({tmp2}):
        {target} = inject_bool(0)
elif is_bool({tmp1}):
    if is_int({tmp2}):
        {target} = inject_bool(0)
    elif is_bool({tmp2}):
        if project_bool({tmp1}) == project_bool({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
"""
    
    else:
        exp_code += f"""
if is_int({tmp1}):
    if is_int({tmp2}):
        if project_int({tmp1}) {op} project_int({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
    elif is_bool({tmp2}):
        if project_int({tmp1}) {op} project_int({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
elif is_bool({tmp1}):
    if is_int({tmp2}):
        if project_int({tmp1}) {op} project_int({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
    elif is_bool({tmp2}):
        if project_int({tmp1}) {op} project_int({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)"""

    return exp_code


def plus_explicate_code(target, left, right, tmp1, tmp2):

    exp_code = f""""""
    if is_explicit_int_or_bool(left):
        l_val = to_int_literal(left)
        exp_code += f"""{tmp1} = inject_int({l_val})\n"""
    else:
        exp_code += f"""{tmp1} = {left}\n"""
    if is_explicit_int_or_bool(right):
        r_val = to_int_literal(right)
        exp_code += f"""{tmp2} = inject_int({r_val})\n"""
    else:
        exp_code += f"""{tmp2} = {right}\n"""
    
    exp_code += f"""
if is_int({tmp1}):
    if is_int({tmp2}):
        {target} = inject_int(project_int({tmp1}) + project_int({tmp2}))
    elif is_bool({tmp2}):
        {target} = inject_int(project_int({tmp1}) + project_int({tmp2}))
elif is_bool({tmp1}):
    if is_int({tmp2}):
        {target} = inject_int(project_int({tmp1}) + project_int({tmp2}))
    elif is_bool({tmp2}):
        {target} = inject_int(project_int({tmp1}) + project_int({tmp2}))"""
    
    # print("\n=========== UNflatteted EXplicate code ========\n")
    # print(exp_code)
    return exp_code


#EXPLICATE TEST ABBREVIATIONS
#====================================================================================

def compare_explicate_code_TEST_ABBREVIATED(target, left, op, right):
    if op == "==":
        return f"""{target} = box_equal({left}, {right})"""
    elif op == "!=":
        return f"""{target} = box_nequal({left}, {right})"""
    elif op == "is":
        return f"""{target} = box_is({left}, {right})"""
    else:
        print(f"Unrecognized operator {op} in compare_explicate_code_TEST_ABBREVIATED()")
        exit(1)


def plus_explicate_code_TEST_ABBREVIATED(target, left, right):
    return f"""{target} = box_add({left}, {right})"""

#====================================================================================


class ExplicateAST():

    def __init__(self, abbreviate=0):
        self.counter = 0
        self.temp_var_prefix = "t_"
        self.abbreviate = abbreviate
    
    def explicate(self, node):

        if isinstance(node, ast.Module):
            return ast.Module(
                body = [self.explicate(child_node) for child_node in node.body],
                type_ignores = []
            )

        elif isinstance(node, list):
            return [self.explicate(elem) for elem in node]

        elif isinstance(node, ast.Expr):
            return self.explicate(node.value)

        elif isinstance(node, ast.Call):
            if is_print(node):
                arg = to_atomic_str(node.args[0])
                return self.print_explicate_node(arg)

        elif isinstance(node, ast.Assign):

            target = node.targets[0].id

            if isinstance(node.value, ast.BinOp):
                if isinstance(node.value.op, ast.Add):
                    left = to_atomic_str(node.value.left)
                    right = to_atomic_str(node.value.right)

                    return self.assign_plus_explicate_node(target, left, right)
            
            elif isinstance(node.value, ast.Compare):

                left = to_atomic_str(node.value.left)
                op = to_op_str(node.value.ops[0])
                right = to_atomic_str(node.value.comparators[0])

                return self.assign_compare_explicate_node(target, left, op, right)
            
            elif is_eval_input(node.value):
                return self.assign_eval_input_explicate_node(target)

            elif is_atomic(node.value):
                right = to_atomic_str(node.value)
                return self.assign_atomic_explicate_node(target, right)

        
        elif isinstance(node, ast.If):
            node = ast.If(test = node.test,
                          body = self.explicate(node.body),
                          orelse = self.explicate(node.orelse))
        return node


    def print_explicate_node(self, arg):
        exp_tree = ast.parse(call_print_explicate_code(arg))
        # exp_tree = flatten(exp_tree, "E_")
        return exp_tree.body

    def assign_eval_input_explicate_node(self, target):
        exp_tree = ast.parse(assign_eval_input_explicate_code(target))
        # exp_tree = flatten(exp_tree, "E_")
        return exp_tree.body

    def assign_atomic_explicate_node(self, target, right):
        exp_tree = ast.parse(assign_atomic_explicate_code(target, right))
        # exp_tree = flatten(exp_tree, "E_")
        return exp_tree.body

    def assign_compare_explicate_node(self, target, left, op, right):

        tmp1 = f"e_temp_{self.counter}"
        tmp2 = f"e_temp_{self.counter + 1}"

        if self.abbreviate:
            exp_tree = ast.parse(compare_explicate_code_TEST_ABBREVIATED(target, left, op, right))
        else:
            exp_tree = ast.parse(compare_explicate_code(target, left, op, right, tmp1, tmp2))
            exp_tree = flatten(exp_tree, "EXP__")
        self.counter += 2

        return exp_tree.body

    def assign_plus_explicate_node(self, target, left, right):

        tmp1 = f"e_temp_{self.counter}"
        tmp2 = f"e_temp_{self.counter + 1}"

        if self.abbreviate:

            exp_tree = ast.parse(plus_explicate_code_TEST_ABBREVIATED(target, left, right))
        else:
            exp_tree = ast.parse(plus_explicate_code(target, left, right, tmp1, tmp2))
            exp_tree = flatten(exp_tree, "EXP__")

        self.counter += 2

        return exp_tree.body



def explicate(flat_tree, abbrev=0):
    return ExplicateAST(abbrev).explicate(flat_tree)




if __name__ == "__main__":

    if (len(sys.argv) < 2):
        print("Usage : python3 flatten_tester.py <python prog> [explicate-abbreviate]")
        exit(1)

    if len(sys.argv) == 3:
        exp_abbrev = (1 if sys.argv[2] == "1" else 0)
    else:
        exp_abbrev = 0

    file = sys.argv[1]

    if not os.path.exists(file):
        print(f"filed '{file}' could not be opened")
        sys.exit(1)
    
    with open(file, 'r') as f:
        prog = f.read()
    
    print("========PROG========")
    print(prog)

    # print("=======ORIGINAL AST======")
    # print(ast.dump(ast.parse(prog), indent=3))

    py_ast = ast.parse(prog)
    py_ast = rename_source_variables(py_ast)
    flat_tree = flatten(py_ast)

    # print("======FLAT TREE=====")
    # print(ast.dump(flat_tree, indent=3))


    print("\n===FLAT PROG====")
    print(un_parse(flat_tree))

    exp_tree = explicate(flat_tree, exp_abbrev)

    # print("\n=========UNflattened Explicate code=======")
    # print(un_parse(exp_tree))

    # print("\n=========flattened Explicate code=======")
    # print(un_parse(exp_tree))

    # print("======EXPLICATED TREE=======")
    # print(ast.dump(exp_tree, indent=3))


    print("\n======EXPLICATED PROG=======")
    print(un_parse(exp_tree))