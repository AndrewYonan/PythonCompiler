import ast
from ast import *


# AST classes
# ===========================================

class Module:
    def __init__(self, body, type_ignores):
        self.body = body
        self.type_ignores = type_ignores
    def __repr__(self):
        return f"Module(body={self.body}, type_ignores={self.type_ignores})"

class Assign:
    def __init__(self, targets, value):
        self.targets = targets
        self.value = value
    def __repr(self):
        return f"Assign(targets={self.targets}, value={self.value})"

class Name:
    def __init__(self, id, ctx):
        self.id = id
        self.ctx = ctx
    def __repr__(self):
        return f"Name(id=\'{self.id}\', ctx={self.ctx})"

class Constant:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Constant(value={self.value})"


class Expr:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Expr(value={self.value})"

class Call:
    def __init__(self, func, args, keywords):
        self.func = func
        self.args = args
        self.keywords = keywords
    def __repr__(self):
        return f"Call(func={self.func}, args={self.args}, keywords={self.keywords})"

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return f"BinOp(left={self.left}, op={self.op}, right={self.right})"

class UnaryOp:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
    def __repr__(self):
        return f"UnaryOp(op={self.op}, operand={self.operand})"

class USub:
    def __repr__(self):
        return "USub()"

class Add:
    def __repr__(self):
        return "Add()"

class Load:
    def __repr__(self):
        return "Load()"


# Utilities
# ===========================================

def takes_single_line(str):
    return "\n" not in str


# AST console dump method (prints the data structure with indents (for testing purposes))
# ===========================================

class ASTDump:
    
    def __init__(self):
        self.indent = " "*4
    
    def dump(self, node, depth=0):

        if isinstance(node, Module):

            body = self.dump(node.body, depth+1)

            type_ignores = self.dump(node.type_ignores, depth+1)

            if takes_single_line(body):
                comma = ","
                nline = ""
                space=0
            else:
                comma = ""
                nline = "\n"
                space=1

            return f"Module({nline}{self.indent*space}body={body}{comma}{" "*(1-space)}{self.indent*space}type_ignores={type_ignores})"

        if isinstance(node, list):

            if len(node) == 0:
                return str(node) 
                
            dump_str = "["

            for i in range(len(node)):
                comma = "" if i == len(node) - 1 else ", "

            for elem in node:
                dump_str += (self.dump(elem, depth+1) + comma)
            dump_str += "]\n"

            return dump_str
        
        if isinstance(node, Expr):
            value = self.dump(node.value, depth+1)
            return f"\n{self.indent*depth}Expr(\n{self.indent*(depth+1)}value={value})" 
    
        if isinstance(node, Constant):
            return f"Constant(value={node.value})"
        
        if isinstance(node, BinOp):

            left = self.dump(node.left, depth+1)
            right = self.dump(node.right, depth+1)
            return f"BinOp(\n{self.indent*(depth+1)}left={left},\n{self.indent*(depth+1)}op={node.op},\n{self.indent*(depth+1)}right={right})"


# tree = Module(
#         body = [Expr(
#             value=Call(
#                 func=Name(id="print", ctx=Load()), 
#                 args=BinOp(left=Constant(1), op=Add(), right=Constant(3)), 
#                 keywords=[]))],
#         type_ignores = []
#     )



if __name__ == "__main__":

    tree = Module(
        body = [Expr(value=BinOp(left=BinOp(left=Constant(1), op=Add(), right=BinOp(left=Constant(1), op=Add(), right=Constant(2))), op=Add(), right=BinOp(left=Constant(3), op=Add(), right=Constant(4)))),
                Expr(value=Constant(1)),
                Expr(value=Constant(1))],
        type_ignores = []
    )

    # tree = Module(
    #     body = [Expr(BinOp(left=BinOp(left=Constant(1), op=Add(), right=Constant(1)), op=Add(), right=BinOp(left=Constant(1), op=Add(), right=Constant(1))))],
    #     type_ignores = []
    # )

    # tree = Module(
    #     body = [],
    #     type_ignores = []
    # )

    prog = """(1+(1+2))+(3+4)
    \n1
    \n1"""


    dumper = ASTDump()
    print(dumper.dump(tree))

    
    
    #print(tree)
    print("\n====FROM AST.dump=====\n")
    tree = ast.parse(prog)
    print(ast.dump(tree, indent=4))