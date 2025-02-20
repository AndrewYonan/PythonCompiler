import ast
from ast import *


def un_parse(py_ast):
    return UnParser().un_parse(py_ast, 0)



class UnParser():

    def __init__(self):
        self.spaces_per_indent = 4

    def un_parse(self, node, indent_level, no_indent=False):

        indent = "" if no_indent else (" " * self.spaces_per_indent) * indent_level

        if isinstance(node, ast.Module):
            return self.un_parse(node.body, indent_level)

        if isinstance(node, ast.BinOp):
            return self.un_parse(node.left, indent_level) + " + " + self.un_parse(node.right, indent_level)
        
        if isinstance(node, ast.UnaryOp):
            return self.un_parse(node.op, indent_level) + "(" + self.un_parse(node.operand, indent_level) + ")"

        if isinstance(node, ast.Expr):
            return indent + self.un_parse(node.value, indent_level) + "\n"
        
        if (isinstance(node, ast.Assign)):
            return indent + node.targets[0].id + " = " + self.un_parse(node.value, indent_level) + "\n"

        if (isinstance(node, ast.Name)):
            return node.id

        if isinstance(node, ast.Constant):
            return str(node.value)
        
        if isinstance(node, ast.USub):
            return "-"

        if (isinstance(node, ast.Call)):
            return node.func.id + "(" + self.un_parse_fun_args(node.args, indent_level) + ")"

        # p0a additions
        #======================================

        if isinstance(node, ast.Not):
            return "not "
        
        if isinstance(node, ast.And):
            return " and "
        
        if isinstance(node, ast.Or):
            return " or "
        
        if isinstance(node, ast.Eq):
            return " == "
        
        if isinstance(node, ast.NotEq):
            return " != "
        
        if isinstance(node, ast.BoolOp):
            return self.un_parse(node.values[0], indent_level) + self.un_parse(node.op, indent_level) + self.un_parse(node.values[1], indent_level)
        
        if (isinstance(node, ast.Compare)):
            return self.un_parse(node.left, indent_level) + self.un_parse(node.ops[0], indent_level) + self.un_parse(node.comparators, indent_level)
        
        if (isinstance(node, ast.While)):
            return indent + "while " + self.un_parse(node.test, indent_level, no_indent=True) + ":\n" + self.un_parse(node.body, indent_level + 1)
        
        if (isinstance(node, ast.If)):
            
            un_parse_str = indent + "if " + self.un_parse(node.test, indent_level, no_indent=True) + ":\n" + self.un_parse(node.body, indent_level + 1)

            if len(node.orelse) > 0:
                un_parse_str += indent + "else:\n" + self.un_parse(node.orelse, indent_level + 1)
            
            return un_parse_str

        if isinstance(node, list):
            un_parse_str = ""
            for elem in node:
                un_parse_str += (self.un_parse(elem, indent_level))
            return un_parse_str


    def un_parse_fun_args(self, args, indent_level):

        un_parse_str = ""

        for arg in args:
            un_parse_str += (self.un_parse(arg, indent_level) + ", ")

        return un_parse_str[:-2]