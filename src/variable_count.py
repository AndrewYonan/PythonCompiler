import ast
from ast import *


def get_ast(prog):
    return ast.parse(prog)


class NameCounter(ast.NodeVisitor):
    def __init__(self):
        self.name_list = []
    def visit(self, node):
        self.generic_visit(node)
        if (isinstance(node, Name)):
            if (node.id != "print" 
                and node.id != "eval" 
                and node.id != "input"
                and node.id not in self.name_list):
                    self.name_list.append(node.id)




def get_var_count(prog):

    name_counter = NameCounter()

    tree = get_ast(prog)
    name_counter.visit(tree)
    return len(name_counter.name_list)


prog1 = """
1 + 2 + eval(input())
"""


if __name__ == "__main__":
    print(f"variable count : {get_var_count(prog1)}")
