import ast
from ast import *


class UnParser():

    def un_parse(self, node):

        un_parse_str = ""

        if isinstance(node, ast.Module):
            for child_node in ast.iter_child_nodes(node):
                un_parse_str += self.un_parse(child_node)

        if isinstance(node, ast.BinOp):
            un_parse_str += self.un_parse(node.left) + " + " + self.un_parse(node.right)
        
        if isinstance(node, ast.UnaryOp):
            un_parse_str += "-(" + self.un_parse(node.operand) + ")"

        if isinstance(node, ast.Expr):
            un_parse_str += (self.un_parse(node.value) + "\n")
        
        if (isinstance(node, ast.Assign)):
            un_parse_str += (node.targets[0].id + " = " + self.un_parse(node.value) + "\n")

        if (isinstance(node, ast.Name)):
            un_parse_str += node.id

        if isinstance(node, ast.Constant):
            un_parse_str += str(node.value)
        
        if isinstance(node, ast.USub):
            un_parse_str += "-"

        if (isinstance(node, ast.Call)):
            un_parse_str += node.func.id + "(" + self.un_parse_fun_args(node.args) + ")"

        
        return un_parse_str
    

    def un_parse_fun_args(self, args):
        un_parse_str = ""
        for arg in args:
            un_parse_str += (self.un_parse(arg) + ", ")
        return un_parse_str[:-2]

