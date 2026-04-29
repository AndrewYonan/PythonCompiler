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
    elif isinstance(node, ast.Not):
        return "not"
    elif isinstance(node, ast.USub):
        return "-"
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

def is_explicit_LIST(str):
    return "[" in str

def is_explicit_int_or_bool(str):
    return is_explicit_BOOL(str) or is_explicit_INT(str)

#===================================================================
# EXPLICATION

def assign_eval_input_explicate_code(target):
    return f"""{target} = eval_input_pyobj()"""

def call_print_explicate_code(arg):
    return f"""print_any({arg})"""

def call_eval_input_explicate_code():
    return f"""eval_input_pyobj()"""

def get_temp_explicate_var_for(elem, tmp1):
    if is_explicit_int_or_bool(elem):
        val = to_int_literal(elem)
        return f"""{tmp1} = inject_int({val})\n"""
    else:
        return f"""{tmp1} = {elem}\n"""

def get_temp_explicate_var_for_list_elem(elem, tmp1):
    if is_explicit_INT(elem):
        return f"""{tmp1} = inject_int({elem})\n"""
    elif is_explicit_BOOL(elem):
        val = to_int_literal(elem)
        return f"""{tmp1} = inject_bool({val})\n"""
    else:
        return f"""{tmp1} = {elem}\n"""

def assign_atomic_explicate_code(target, right):
    exp_code = f""""""
    if is_explicit_INT(right):
        r_val = to_int_literal(right)
        exp_code += f"""{target} = inject_int({r_val})\n"""
    elif is_explicit_BOOL(right):
        r_val = to_int_literal(right)
        exp_code += f"""{target} = inject_bool({r_val})\n"""
    else:
        exp_code += f"""{target} = {right}\n"""
    return exp_code


def compare_explicate_code(target, left, op, right, tmp1, tmp2):

    exp_code = get_temp_explicate_var_for(left, tmp1)
    exp_code += get_temp_explicate_var_for(right, tmp2)

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
    elif is_big({tmp2}):
        {target} = inject_bool(0)
elif is_bool({tmp1}):
    if is_int({tmp2}):
        {target} = inject_bool(0)
    elif is_bool({tmp2}):
        if project_bool({tmp1}) == project_bool({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
    elif is_big({tmp2}):
        {target} = inject_bool(0)
elif is_big({tmp1}):
    {target} = inject_bool(0)
"""
    
    elif op == "==":
        exp_code += f"""
if is_int({tmp1}):
    if is_int({tmp2}):
        if project_int({tmp1}) == project_int({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
    elif is_bool({tmp2}):
        if project_int({tmp1}) == project_bool({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
elif is_bool({tmp1}):
    if is_int({tmp2}):
        if project_bool({tmp1}) == project_int({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
    elif is_bool({tmp2}):
        if project_bool({tmp1}) == project_bool({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
elif is_big({tmp1}):
    if is_big({tmp2}):
        {target} = inject_bool(equal(project_big({tmp1}), project_big({tmp2})))
    else:
        {target} = inject_bool(0)
"""
    
    elif op == "!=":
        exp_code += f"""
if is_int({tmp1}):
    if is_int({tmp2}):
        if project_int({tmp1}) != project_int({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
    elif is_bool({tmp2}):
        if project_int({tmp1}) != project_bool({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
elif is_bool({tmp1}):
    if is_int({tmp2}):
        if project_bool({tmp1}) != project_int({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
    elif is_bool({tmp2}):
        if project_bool({tmp1}) != project_bool({tmp2}):
            {target} = inject_bool(1)
        else:
            {target} = inject_bool(0)
elif is_big({tmp1}):
    if is_big({tmp2}):
        {target} = inject_bool(not_equal(project_big({tmp1}), project_big({tmp2})))
    else:
        {target} = inject_bool(1)
"""
    
    else:
        print(f"Unknown operator {op} in compare_explicate_code()")
        exit(1)

    return exp_code


def plus_explicate_code(target, left, right, tmp1, tmp2):

    exp_code = get_temp_explicate_var_for(left, tmp1)
    exp_code += get_temp_explicate_var_for(right, tmp2)

    exp_code += f"""
if is_int({tmp1}):
    if is_int({tmp2}):
        {target} = inject_int(project_int({tmp1}) + project_int({tmp2}))
    elif is_bool({tmp2}):
        {target} = inject_int(project_int({tmp1}) + project_bool({tmp2}))
elif is_bool({tmp1}):
    if is_int({tmp2}):
        {target} = inject_int(project_bool({tmp1}) + project_int({tmp2}))
    elif is_bool({tmp2}):
        {target} = inject_int(project_bool({tmp1}) + project_bool({tmp2}))
elif is_big({tmp1}):
    if is_big({tmp2}):
        {target} = inject_big(add(project_big({tmp1}), project_big({tmp2})))"""
    
    return exp_code


def unary_explicate_code(target, op, right, tmp1):

    exp_code = get_temp_explicate_var_for(right, tmp1)

    if op == "not":
        exp_code += f"""
if is_int({tmp1}):
    if project_int({tmp1}) == 0:
        {target} = inject_bool(1)
    else:
        {target} = inject_bool(0)
elif is_bool({tmp1}):
    if project_bool({tmp1}) == 0:
        {target} = inject_bool(1)
    else:
        {target} = inject_bool(0)
elif is_big({tmp1}):
    if is_true({tmp1}):
        {target} = inject_bool(0)
    else:
        {target} = inject_bool(1)"""

    elif op == "-":
        exp_code += f"""
if is_int({tmp1}):
    {target} = inject_int(-project_int({tmp1}))
elif is_bool({tmp1}):
    {target} = inject_int(-project_bool({tmp1}))
"""

    return exp_code


def int_cast_explicate_code(target, arg, tmp1):
    exp_code = get_temp_explicate_var_for(arg, tmp1)
    exp_code += f"""
if is_int({tmp1}):
    {target} = inject_int(project_int({tmp1}))
elif is_bool({tmp1}):
    {target} = inject_int(project_bool({tmp1}))"""
    return exp_code


def assign_list_explicate_code(target, lst_elems, tmps):

    exp_code = f""""""

    for i in range(len(lst_elems)):
        exp_code += get_temp_explicate_var_for_list_elem(lst_elems[i], tmps[i])
        
    exp_code += f"""{target} = inject_big(create_list(inject_int({len(lst_elems)})))\n"""

    for i in range(len(lst_elems)):
        exp_code += f"""set_subscript({target}, inject_int({i}), {tmps[i]})\n"""

    return exp_code


def assign_dict_explicate_code(target, key_elems, val_elems, key_temp_vars, val_temp_vars):

    exp_code = f""""""

    for i in range(len(key_elems)):
        exp_code += get_temp_explicate_var_for_list_elem(key_elems[i], key_temp_vars[i])
        exp_code += get_temp_explicate_var_for_list_elem(val_elems[i], val_temp_vars[i])

    exp_code += f"""{target} = inject_big(create_dict())\n"""
    
    for i in range(len(key_elems)):
        exp_code += f"""set_subscript({target}, {key_temp_vars[i]}, {val_temp_vars[i]})\n"""
    
    return exp_code


def assign_get_subscript_explicate_code(target, lst_name, key, tmp_key):

    exp_code = f""""""
        
    if is_explicit_int_or_bool(key):
        exp_code += get_temp_explicate_var_for(key, tmp_key)
        key = tmp_key
    
    exp_code += f"""{target} = get_subscript({lst_name}, {key})"""
    return exp_code

def assign_list_entry_explicate_code(target_lst, key, val, tmp_key, tmp_val):

    exp_code = f""""""

    if is_explicit_int_or_bool(key):
        exp_code += get_temp_explicate_var_for(key, tmp_key)
        key = tmp_key

    if is_explicit_int_or_bool(val):
        exp_code += get_temp_explicate_var_for_list_elem(val, tmp_val)
        exp_code += f"""set_subscript({target_lst}, {key}, {tmp_val})"""
    else:
        exp_code += f"""set_subscript({target_lst}, {key}, {val})"""

    return exp_code


#EXPLICATE TEST ABBREVIATIONS (for more stream-lined testing)
#====================================================================================

def compare_explicate_code_TEST_ABBREVIATED(target, left, op, right, tmp1, tmp2):
    
    exp_code = get_temp_explicate_var_for(left, tmp1)
    exp_code += get_temp_explicate_var_for(right, tmp2)

    if op == "==":
        exp_code += f"""{target} = box_equal({tmp1}, {tmp2})"""
    elif op == "!=":
        exp_code += f"""{target} = box_nequal({tmp1}, {tmp2})"""
    elif op == "is":
        exp_code += f"""{target} = box_is({tmp1}, {tmp2})"""
    else:
        print(f"Unrecognized operator {op} in compare_explicate_code_TEST_ABBREVIATED()")
        exit(1)
    
    return exp_code


def plus_explicate_code_TEST_ABBREVIATED(target, left, right, tmp1, tmp2):

    exp_code = get_temp_explicate_var_for(left, tmp1)
    exp_code += get_temp_explicate_var_for(right, tmp2)
    exp_code += f"""{target} = box_add({tmp1}, {tmp2})"""

    return exp_code


def unary_explicate_code_TEST_ABBREVIATED(target, op, right, tmp1):

    exp_code = get_temp_explicate_var_for(right, tmp1)
    if op == "not":
        exp_code += f"""{target} = box_not({tmp1})"""
    elif op == "-":
        exp_code += f"""{target} = box_unary_sub({tmp1})"""
    else:
        print(f"unrecognized operator {op} in unary_explicate_TEST_ABBREV()")
        exit(1)
    return exp_code

def int_cast_explicate_code_TEST_ABBERVIATED(target, arg, tmp1):

    exp_code = get_temp_explicate_var_for(arg, tmp1)
    exp_code += f"""{target} = box_int({tmp1})"""

    return exp_code

#====================================================================================


class ExplicateAST():

    def __init__(self, abbreviate=0):
        self.counter = 0
        self.flatten_temp_prefix = "E_"
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

        elif isinstance(node, ast.BinOp):
            return []
        
        elif isinstance(node, ast.UnaryOp):
            return []
        
        elif isinstance(node, ast.Constant):
            return []

        elif isinstance(node, ast.If):
            return self.if_explicate_node(node)

        elif isinstance(node, ast.While):
            return self.while_explicate_node(node)

        elif isinstance(node, ast.Call):

            if is_print(node):
                arg = to_atomic_str(node.args[0])
                return self.print_explicate_node(arg)

            if is_eval_input(node):
                return self.eval_input_explicate_node()


        elif isinstance(node, ast.Assign):

            if isinstance(node.targets[0], ast.Subscript):

                l_val = node.targets[0]
                target_lst = to_atomic_str(l_val.value)
                key = to_atomic_str(l_val.slice)
                val = to_atomic_str(node.value)

                print(f"target_lst = {target_lst}, key = {key}, val = {val}")
                return self.assign_list_entry_explicate_node(target_lst, key, val)

            
            target = node.targets[0].id

            if isinstance(node.value, ast.Expr):
                node.value = node.value.value

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
            
            elif isinstance(node.value, ast.UnaryOp):

                right = to_atomic_str(node.value.operand)
                op = to_op_str(node.value.op)
                return self.assign_unary_explicate_node(target, op, right)

            elif isinstance(node.value, ast.List):
                return self.assign_list_explicate_node(target, node.value)

            elif isinstance(node.value, ast.Dict):
                return self.assign_dict_explicate_node(target, node.value)
            
            elif isinstance(node.value, ast.Subscript):
                return self.assign_get_subscript_explicate_node(target, node.value)
            
            elif is_eval_input(node.value):
                return self.assign_eval_input_explicate_node(target)

            elif is_int_cast(node.value):
                arg = to_atomic_str(node.value.args[0])
                return self.assign_int_cast_explicate_node(target, arg)

            elif is_atomic(node.value):
                right = to_atomic_str(node.value)
                return self.assign_atomic_explicate_node(target, right)

        return node

    def eval_input_explicate_node(self):
        exp_tree = ast.parse(call_eval_input_explicate_code())
        return exp_tree.body 

    def print_explicate_node(self, arg):
        exp_tree = ast.parse(call_print_explicate_code(arg))
        return exp_tree.body

    def assign_eval_input_explicate_node(self, target):
        exp_tree = ast.parse(assign_eval_input_explicate_code(target))
        return exp_tree.body

    def assign_atomic_explicate_node(self, target, right):
        exp_tree = ast.parse(assign_atomic_explicate_code(target, right))
        return exp_tree.body

    def assign_list_explicate_node(self, target, node):

        lst_elems = list(map(lambda x : to_atomic_str(x), node.elts))
        temp_vars = [f"e_temp_{self.counter + i}" for i in range(len(lst_elems))]

        self.counter += len(node.elts)
        exp_tree = ast.parse(assign_list_explicate_code(target, lst_elems, temp_vars))
        exp_tree = flatten(exp_tree, self.flatten_temp_prefix)

        return exp_tree.body

    def assign_dict_explicate_node(self, target, node):

        key_elems = list(map(lambda x : to_atomic_str(x), node.keys))
        val_elems = list(map(lambda x : to_atomic_str(x), node.values))

        key_temp_vars = [f"e_temp_{self.counter + i}" for i in range(len(key_elems))]
        self.counter += len(key_elems)

        val_temp_vars = [f"e_temp_{self.counter + i}" for i in range(len(key_elems))]
        self.counter += len(key_elems)
        
        exp_tree = ast.parse(assign_dict_explicate_code(target, key_elems, val_elems, key_temp_vars, val_temp_vars))

        exp_tree = flatten(exp_tree, self.flatten_temp_prefix)

        return exp_tree.body


    def assign_list_entry_explicate_node(self, target_lst, key, val): # a[1] = x

        tmp_key = f"e_temp_{self.counter}"
        tmp_val = f"e_temp_{self.counter + 1}"
        self.counter += 2
        exp_tree = ast.parse(assign_list_entry_explicate_code(target_lst, key, val, tmp_key, tmp_val))
        return exp_tree.body

    def assign_get_subscript_explicate_node(self, target, node): # x = a[1]

        tmp_key = f"e_temp_{self.counter}"
        self.counter += 1

        lst_name = to_atomic_str(node.value)
        key = to_atomic_str(node.slice)
        exp_tree = ast.parse(assign_get_subscript_explicate_code(target, lst_name, key, tmp_key))
        exp_tree = flatten(exp_tree, self.flatten_temp_prefix)

        return exp_tree.body

    def assign_compare_explicate_node(self, target, left, op, right):

        tmp1 = f"e_temp_{self.counter}"
        tmp2 = f"e_temp_{self.counter + 1}"

        if self.abbreviate:
            exp_tree = ast.parse(compare_explicate_code_TEST_ABBREVIATED(target, left, op, right, tmp1, tmp2))
        else:
            exp_tree = ast.parse(compare_explicate_code(target, left, op, right, tmp1, tmp2))
            exp_tree = flatten(exp_tree, self.flatten_temp_prefix)

        self.counter += 2

        return exp_tree.body

    def assign_plus_explicate_node(self, target, left, right):

        tmp1 = f"e_temp_{self.counter}"
        tmp2 = f"e_temp_{self.counter + 1}"

        if self.abbreviate:
            exp_tree = ast.parse(plus_explicate_code_TEST_ABBREVIATED(target, left, right, tmp1, tmp2))
        else:
            exp_tree = ast.parse(plus_explicate_code(target, left, right, tmp1, tmp2))
            exp_tree = flatten(exp_tree, self.flatten_temp_prefix)

        self.counter += 2

        return exp_tree.body

    def assign_unary_explicate_node(self, target, op, right):

        tmp1 = f"e_temp_{self.counter}"

        if self.abbreviate:
            exp_tree = ast.parse(unary_explicate_code_TEST_ABBREVIATED(target, op, right, tmp1))
        else:
            exp_tree = ast.parse(unary_explicate_code(target, op, right, tmp1))
            exp_tree = flatten(exp_tree, self.flatten_temp_prefix)

        self.counter += 1
        
        return exp_tree

    def assign_int_cast_explicate_node(self, target, arg):

        tmp1 = f"e_temp_{self.counter}"

        if self.abbreviate:
            exp_tree = ast.parse(int_cast_explicate_code_TEST_ABBERVIATED(target, arg, tmp1))
        else:
            exp_tree = ast.parse(int_cast_explicate_code(target, arg, tmp1))
            exp_tree = flatten(exp_tree, self.flatten_temp_prefix)

        self.counter += 1
        
        return exp_tree.body

    def if_explicate_node(self, node):

        test = to_atomic_str(node.test)
        tmp1 = f"e_temp_{self.counter}"
        self.counter += 1

        test_node = ast.parse(f"""{tmp1} = is_true({test})""")

        if_node = ast.If(
            test = ast.Name(id = tmp1, ctx = Load()),
            body = self.explicate(node.body),
            orelse = self.explicate(node.orelse)
        )

        return [test_node, if_node]

    def while_explicate_node(self, node):

        test = to_atomic_str(node.test)
        tmp1 = f"e_temp_{self.counter}"
        self.counter += 1

        test_node = ast.parse(f"""{tmp1} = is_true({test})""")

        while_node = ast.While(
            test = ast.Name(id = tmp1, ctx = Load()),
            body = self.explicate(node.body + [test_node])
        )

        return [test_node, while_node]


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

    print("=======ORIGINAL AST======")
    print(ast.dump(ast.parse(prog), indent=3))

    py_ast = ast.parse(prog)
    py_ast = rename_source_variables(py_ast)
    flat_tree = flatten(py_ast)

    # print("======FLAT TREE=====")
    # print(ast.dump(flat_tree, indent=3))

    print("\n===FLAT PROG====")
    print(un_parse(flat_tree))

    exp_tree = explicate(flat_tree, exp_abbrev)

    # print("======EXPLICATED TREE=======")
    # print(ast.dump(exp_tree, indent=3))


    print("\n======EXPLICATED PROG=======")
    print(un_parse(exp_tree))