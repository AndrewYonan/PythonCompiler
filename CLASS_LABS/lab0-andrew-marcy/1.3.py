#!/usr/bin/env python3.10
import ast
import sys
from ast import *


def get_ast(prog_code):
    return ast.parse(prog_code)


#The following are 3 separate strategies
#for printing all Name nodes in a python program AST


#AST-WALK METHOD
def print_ast_names_walk(prog):
    AST = get_ast(prog)
    for n in ast.walk(AST):
        if isinstance(n, ast.Name):
            print(f"Name : {n.id}")


#VISITOR METHOD
class ASTVisitorMethods(ast.NodeVisitor):
    def visit_Name(self, node):
        print(f"Name : {node.id}")
        self.generic_visit(node)


def print_ast_names_visitor(prog):
    AST = get_ast(prog)
    ASTVisitorMethods().visit(AST)


#RECURSIVE METHOD
def print_ast_names_recursive(n):
    if (isinstance(n, Module)):
        for x in n.body:
            print_ast_names_recursive(x)
    if (isinstance(n, Assign)):
        for x in n.targets:
            print(f"Name : {x.id}")
        print_ast_names_recursive(n.value)
    if (isinstance(n, Expr)):
        print_ast_names_recursive(n.value)
    if (isinstance(n, Name)):
        print(f"Name : {n.id}")
    if (isinstance(n, BinOp)):
        print_ast_names_recursive(n.left)
        print_ast_names_recursive(n.right)
    if (isinstance(n, UnaryOp)):
        print_ast_names_recursive(n.operand)
    if(isinstance(n, Call)):
        print_ast_names_recursive(n.func)
        for x in n.args:
            print_ast_names_recursive(x)





def process_p0_prog(prog):

    tree = get_ast(prog)

    print(f"P0-PROG:\n {prog}\n")
    print(f"Prog AST TREE:\n {ast.dump(tree,indent=3)}\n")

    print("\nAST-walk:")
    print_ast_names_walk(prog)
    print("\nAST-visitor:")
    print_ast_names_visitor(prog)
    print("\nAST-resursive:")
    print_ast_names_recursive(get_ast(prog))



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
