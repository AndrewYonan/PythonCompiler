import ast
from ast import *


def un_parse(py_ast):
    return UnParser().un_parse(py_ast, 0)


class UnParser():

    def __init__(self):
        self.spaces_per_indent = 4

    def un_parse(self, node, indent_level, no_indent=False):

        un_parse_str = ""
        indent = "" if no_indent else (" " * self.spaces_per_indent) * indent_level

        if isinstance(node, ast.Module):
            for child_node in ast.iter_child_nodes(node):
                un_parse_str += self.un_parse(child_node, indent_level)

        if isinstance(node, ast.BinOp):
            un_parse_str += self.un_parse(node.left, indent_level) + " + " + self.un_parse(node.right, indent_level)
        
        if isinstance(node, ast.UnaryOp):
            un_parse_str += "-(" + self.un_parse(node.operand, indent_level) + ")"

        if isinstance(node, ast.Expr):
            un_parse_str += (self.un_parse(node.value, indent_level) + "\n")
        
        if (isinstance(node, ast.Assign)):
            un_parse_str += (node.targets[0].id + " = " + self.un_parse(node.value, indent_level) + "\n")

        if (isinstance(node, ast.Name)):
            un_parse_str += node.id

        if isinstance(node, ast.Constant):
            un_parse_str += str(node.value)
        
        if isinstance(node, ast.USub):
            un_parse_str += "-"

        if (isinstance(node, ast.Call)):
            un_parse_str += indent + node.func.id + "(" + self.un_parse(node.args, indent_level) + ")"

        # p0a additions
        if isinstance(node, list):
            un_parse_str = ""
            for elem in node:
                un_parse_str += (self.un_parse(elem, indent_level) + ", ")
            return un_parse_str[:-2]
        
        if (isinstance(node, ast.Compare)):

            cmp = "==" if isinstance(node.ops[0], ast.Eq) else "!="
            un_parse_str += self.un_parse(node.left, indent_level) + f" {cmp} " + self.un_parse(node.comparators, indent_level)

        if (isinstance(node, ast.If)):

            un_parse_str += indent + "if " + self.un_parse(node.test, indent_level, no_indent=True) + ":\n" + self.un_parse(node.body, indent_level + 1)

            if len(node.orelse) > 0:
                un_parse_str += indent + "else:\n" + self.un_parse(node.orelse, indent_level + 1)

        
        return un_parse_str
    
