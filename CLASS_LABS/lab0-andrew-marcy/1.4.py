#!/usr/bin/env python3.10
#adding parent field to AST nodes

#NOTES from class
#de-singletonize all tokens first (python AST tokens are by default singletonized), in
#in order to add a parent field


import ast
from ast import *

def to_str(node):
    if isinstance(node, ast.Name):
        return "(" + node.id + ")"
    elif isinstance(node, ast.Constant):
        return "(" + str(node.value) + ")"
    elif isinstance(node, ast.Add):
        return "(+)"
    elif isinstance(node, ast.USub):
        return "(-)"
    elif isinstance(node, ast.Assign):
        return "(" + node.targets[0].id + " =)"
    else:
        return ""


class AddParentTester(ast.NodeVisitor):
    def visit(self, node):
        print(f"Node {node} {to_str(node)} has parent : {node.parent} {to_str(node.parent)}")
        self.generic_visit(node)


def get_ast(prog):
    return ast.parse(prog)


class AddParent(ast.NodeTransformer):
    
    def visit_Module(self, node):
        for x in node.body:
            x.parent = node
        self.generic_visit(node)
        node.parent = None
        return node

    def visit_Assign(self, node):
        for x in node.targets:
            x.ctx.parent = node
            x.parent = node
        node.value.parent = node
        self.generic_visit(node)
        return node

    def visit_Expr(self, node):
        node.value.parent = node
        self.generic_visit(node)
        return node

    def visit_BinOp(self, node):
        node.left.parent = node
        node.op.parent = node
        node.right.parent = node
        self.generic_visit(node)
        return node
    
    def visit_Name(self, node):
        node.ctx.parent = node
        self.generic_visit(node)
        return node

    def visit_UnaryOp(self, node):
        node.op.parent = node
        node.operand.parent = node
        self.generic_visit(node)
        return node

    def visit_Call(self, node):
        node.func.parent = node
        for arg_node in node.args:
            arg_node.parent = node
        self.generic_visit(node)
        return node



def process_p0_prog(prog):

    tree = get_ast(prog)
    print(f"\n===PROG=== :\n {prog}")
    print(f"\n===Prog AST TREE===:\n {ast.dump(tree,indent=3)}\n")
    parented_tree = AddParent().visit(tree)


    print(f"\n===CHILD-PARENT PAIRS===:")
    AddParentTester().visit(parented_tree)



if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage : python3 <prog> <P0 program as file>")
        exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, 'r') as file:
            prog = file.read()
            process_p0_prog(prog)
    
    except FileNotFoundError:
        print(f"Error : The file '{filename}' does not exist.")

            
    