import sys
import os
import ast
from ast import *
from unparser import *


class RenameVariables(ast.NodeTransformer):
    def visit(self, node):
        self.generic_visit(node)
        if isinstance(node, ast.Name):
            if node.id != "print" and node.id != "eval" and node.id != "input":
                return ast.Name(
                    id = "s_" + node.id,
                    ctx = node.ctx
                )
        return node


def rename_source_variables(py_prog_ast):
    return RenameVariables().visit(py_prog_ast)


def is_simple_BinOp(node):
    if isinstance(node, ast.BinOp):
        return (isinstance(node.left, ast.Constant) or isinstance(node.left, ast.Name)) and (isinstance(node.right, ast.Constant) or (isinstance(node.right, ast.Name)))
    return False



def is_simple_UnaryOp(node):
    if isinstance(node, ast.UnaryOp):
        return isinstance(node.operand, ast.Constant) or isinstance(node.operand, ast.Name)
    return False



def is_simple_Expr(node):
    return isinstance(node, ast.Constant) or is_simple_BinOp(node) or is_simple_UnaryOp(node)



def is_simple_statement(node):

    if isinstance(node, ast.Assign):
        return is_simple_Expr(node.value)
    
    if isinstance(node, ast.BinOp):
        return is_simple_BinOp(node)
    
    if isinstance(node, ast.UnaryOp):
        return is_simple_UnaryOp(node)

    if isinstance(node, ast.Expr):
        return is_simple_BinOp(node) or is_simple_UnaryOp(node)
    
    if isinstance(node, ast.Constant):
        return True
    
    if isinstance(node, ast.Name):
        if node.id != "print" and node.id != "eval":
            return True



def is_atomic(node):
    if isinstance(node, ast.Constant):
        return True
    elif isinstance(node, ast.Name):
        if node.id != "eval" and node.id != "input":
            return True



def is_eval_input(node):
    if isinstance(node, ast.Call):
        if node.func.id == "eval":
            if node.args[0].func.id == "input":
                return True



def new_assign_node(node, temp_id):
    if is_simple_BinOp(node) or is_simple_UnaryOp(node) or is_eval_input(node):
        return ast.Assign(targets = [Name(id = temp_id, ctx = Store())],
                          value = node)



class FlattenAST():

    def __init__(self):

        self.counter = 0 
        self.flattened_body = [] 

    def flatten(self, node):

        if isinstance(node, ast.Module):

            for child_node in ast.iter_child_nodes(node):
                self.flatten(child_node)
                self.flattened_body.append(child_node)

        elif is_simple_statement(node):
            return


        elif isinstance(node, ast.Assign):
            self.flatten(node.value)


        elif isinstance(node, ast.Expr):
            self.flatten(node.value)


        elif isinstance(node, ast.BinOp):

            self.flatten(node.left)
            
            if not is_atomic(node.left):
                node.left = self.get_temp_assign_node(node.left)
                
            self.flatten(node.right)

            if not is_atomic(node.right):
                node.right = self.get_temp_assign_node(node.right)
        
        elif isinstance(node, ast.UnaryOp):

            self.flatten(node.operand)

            if not is_atomic(node.operand):
                node.operand = self.get_temp_assign_node(node.operand)
                

        elif isinstance(node, ast.Call):

            if is_eval_input(node):
                return

            for i, arg in enumerate(node.args):
                self.flatten(arg)

                if not is_atomic(arg):
                    node.args[i] = self.get_temp_assign_node(arg)


    def get_temp_assign_node(self, node):
        temp_id = f"temp_{self.counter}"
        self.counter = self.counter + 1
        self.flattened_body.append(new_assign_node(node, temp_id))
        return ast.Name(id = temp_id, ctx = Load())




def flatten_ast(tree):

    flattener = FlattenAST()
    flattener.flatten(tree)

    return ast.Module(
        body = flattener.flattened_body,
        type_ignores = tree.type_ignores
    )




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
