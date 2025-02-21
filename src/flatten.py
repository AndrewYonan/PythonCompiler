import sys
import os
import ast
from ast import *
from unparser import *


class RenameVariables(ast.NodeTransformer):
    def visit(self, node):
        self.generic_visit(node)
        if isinstance(node, ast.Name):
            if node.id != "print" and node.id != "eval" and node.id != "input" and node.id != "int":
                return ast.Name(
                    id = "s_" + node.id,
                    ctx = node.ctx
                )
        return node


def rename_source_variables(py_prog_ast):
    return RenameVariables().visit(py_prog_ast)



def is_atomic(node):
    if isinstance(node, ast.Constant):
        return True
    elif isinstance(node, ast.Name):
        if node.id != "eval" and node.id != "input":
            return True
    return False


def is_simple_BinOp(node):
    if isinstance(node, ast.BinOp):
        return is_atomic(node.left) and is_atomic(node.right)
    return False



def is_simple_UnaryOp(node):
    if isinstance(node, ast.UnaryOp):
        return is_atomic(node.operand)
    return False


def is_simple_BoolOp(node):
    if isinstance(node, ast.BoolOp):
        return is_atomic(node.values[0]) and is_atomic(node.values[1])

def is_simple_compare(node):
    if isinstance(node, ast.Compare):
        return is_atomic(node.left) and is_atomic(node.comparators[0])


def is_simple_Expr(node):
    t = is_atomic(node)
    t = t or is_simple_BinOp(node)
    t = t or is_simple_BoolOp(node)
    t = t or is_simple_UnaryOp(node)
    t = t or is_simple_compare(node)
    return t


def is_eval_input(node):
    if isinstance(node, ast.Call):
        if node.func.id == "eval":
            if node.args[0].func.id == "input":
                return True


def is_int_cast(node):
    if isinstance(node, ast.Call):
        return node.func.id == "int" 


def is_print(node):
    if isinstance(node, ast.Call):
        return node.func.id == "print"
    

class FlattenAST():

    def __init__(self):

        self.counter = 0 

    def flatten(self, node, suite=None):

        if isinstance(node, ast.Module):

            body_suite = []

            for child_node in node.body:

                flat_child = self.flatten(child_node, body_suite)
                body_suite.append(flat_child)
            
            return ast.Module(
                body = body_suite,
                type_ignores = []
            )

        elif isinstance(node, ast.Assign):
            node.value = self.flatten(node.value, suite)

        elif isinstance(node, ast.Expr):
            node.value = self.flatten(node.value, suite)

        elif isinstance(node, ast.BinOp):

            node.left = self.flatten(node.left, suite)
            
            if not is_atomic(node.left):
                node.left = self.get_temp_assign_node(node.left, suite)
                
            node.right = self.flatten(node.right, suite)

            if not is_atomic(node.right):
                node.right = self.get_temp_assign_node(node.right, suite)

        elif isinstance(node, ast.BoolOp):

            node.values[0] = self.flatten(node.values[0], suite)
            
            if not is_atomic(node.values[0]):
                node.values[0] = self.get_temp_assign_node(node.values[0], suite)

            node.values[1] = self.flatten(node.values[1], suite)

            if not is_atomic(node.values[1]):
                node.values[1] = self.get_temp_assign_node(node.values[1], suite)
        
        elif isinstance(node, ast.Compare):

            node.left = self.flatten(node.left, suite)

            if not is_atomic(node.left):
                node.left = self.get_temp_assign_node(node.left, suite)
            
            node.comparators[0] = self.flatten(node.comparators[0], suite)

            if not is_atomic(node.comparators[0]):
                node.comparators[0] = self.get_temp_assign_node(node.comparators[0], suite)
        
        elif isinstance(node, ast.UnaryOp):

            node.operand = self.flatten(node.operand, suite)

            if not is_atomic(node.operand):
                node.operand = self.get_temp_assign_node(node.operand, suite)
                
        elif isinstance(node, ast.Call):
            
            if is_int_cast(node):

                node.args[0] = self.flatten(node.args[0], suite)

            if is_print(node):

                node.args[0] = self.flatten(node.args[0], suite)

                if not is_atomic(node.args[0]):

                    node.args[0] = self.get_temp_assign_node(node.args[0], suite)
        
        elif isinstance(node, ast.If):

            node.test = self.flatten(node.test, suite)

            if not is_atomic(node.test):
                node.test = self.get_temp_assign_node(node.test, suite)

            if_suite = []           
            else_suite = []
        
            for child_node in node.body:
                child_node = self.flatten(child_node, if_suite)
                if_suite.append(child_node)
            node.body = if_suite

            if isinstance(node.orelse, list):
                if len(node.orelse) == 0:
                    return
                for child_node in node.orelse:
                    child_node = self.flatten(child_node, else_suite)
                    else_suite.append(child_node)
                node.orelse = else_suite

            else:
                node.orelse = self.flatten(node.orelse, else_suite)
                else_suite.append(node.orelse)

        elif isinstance(node, ast.While):

            test_suite = []

            node.test = self.flatten(node.test, test_suite)

            if not is_atomic(node.test):
                node.test = self.get_temp_assign_node(node.test, test_suite)
            
            for elem in test_suite:
                suite.append(elem)

            while_suite = []

            for child_node in node.body:
                child_node = self.flatten(child_node, while_suite)
                while_suite.append(child_node)

            for elem in test_suite:
                while_suite.append(elem)
                
            node.body = while_suite
        
        elif isinstance(node, ast.IfExp):
            
            self.flatten(node.test, suite)
            node.test = self.get_temp_assign_node(node.test, suite)

            self.flatten(node.body, suite)
            node.body = self.get_temp_assign_node(node.body, suite)

            self.flatten(node.orelse, suite)
            node.orelse = self.get_temp_assign_node(node.orelse, suite)

            node = self.get_temp_assign_node(node, suite)

        return node
                

    def get_temp_assign_node(self, node, suite):
        if isinstance(node, ast.IfExp):
            return self.get_temp_assign_node_if_exp(node, suite)
        else:
            return self.get_temp_assign_node_regular(node, suite)

    
    def get_temp_assign_node_regular(self, node, suite):
        temp_id = f"temp_{self.counter}"
        self.counter = self.counter + 1
        suite.append(ast.Assign(targets = [Name(id = temp_id, ctx = Store())], value = node))
        return ast.Name(id = temp_id, ctx = Load())
    

    def get_temp_assign_node_if_exp(self, node, suite):

        temp_id = f"temp_{self.counter}"
        self.counter = self.counter + 1
        suite.append(ast.If(
            test = node.test,
            body = ast.Assign(
                targets = [ast.Name(id = temp_id)],
                value = node.body
            ),
            orelse = ast.Assign(
                targets = [ast.Name(id = temp_id)],
                value = node.orelse
            )
        ))
        return ast.Name(id = temp_id, ctx = Load())



def flatten(tree):
    return FlattenAST().flatten(tree)



if __name__ == "__main__":

    if (len(sys.argv) < 2):
        print("Usage : python3 flatten_tester.py <python prog>")
        exit(1)

    file = sys.argv[1]

    if not os.path.exists(file):
        print(f"filed '{file}' could not be opened")
        sys.exit(1)
    
    with open(file, 'r') as f:
        prog = f.read()
    
    print("========PROG========")
    print(prog)

    py_ast = ast.parse(prog)

    print("====AST PROG=====")
    print(ast.dump(py_ast, indent=4))

    print("====Unparsed result=====")
    print(un_parse(py_ast))

    py_ast = rename_source_variables(py_ast)

    print("====renamed vars=====")
    print(un_parse(py_ast))

    flat_tree = flatten(py_ast)

    # print("====FLAT TREE=====")
    # print(ast.dump(flat_tree, indent=4))

    print("===FLAT PROG====")
    print(un_parse(flat_tree))
