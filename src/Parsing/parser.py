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

            if takes_single_line(body):
                comma = ","
                nline = ""
                space=0
            else:
                comma = ""
                nline = "\n"
                space=1

            return f"Module({nline}{self.indent*space}body={body}{comma}{" "*(1-space)}{self.indent*space}{nline}{self.indent*space}type_ignores={node.type_ignores})"

        if isinstance(node, list):

            dump_str = ""

            if len(node) == 0:
                return str(node) 
            
            s1 = self.indent * (depth + 1)
            
            for elem in node:
                
                str_elem = self.dump(elem, depth + 1)
                nline = "" if takes_single_line(str_elem) else "\n"
                dump_str += f"[{nline}{s1}{str_elem}" 
            
            return dump_str + "]"
        
        if isinstance(node, Expr):
            s1 = self.indent * depth
            value = self.dump(node.value, depth+1)
            return f"Expr(\n{self.indent*(depth+1)}value={value})" 
    
        if isinstance(node, Constant):
            return f"Constant(value={node.value})"
        
        if isinstance(node, BinOp):
            left = self.dump(node.left, depth+1)
            right = self.dump(node.right, depth+1)
            return f"BinOp(\n{self.indent*(depth+1)}left={left},\n{self.indent*(depth+1)}op={node.op},\n{self.indent*(depth+1)}right={right})"
        
        if isinstance(node, Call):
            s1 = self.indent * depth
            s2 = self.indent * (depth + 1)
            args = self.dump(node.args, depth + 1)
            return f"Call(\n{s2}func={node.func},\n{s2}args={args}{s2}\n{s2}keywords={node.keywords})"


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
                Expr(value=Constant(1)),
                Expr(BinOp(left=Constant(112), op=Add(), right=Call(Name(id="eval", ctx=Load()), args=[Call(Name(id="input", ctx=Load()), args=[], keywords=[])], keywords=[])))],
        type_ignores = []
    )

    # tree = Module(
    #     body = [Expr(Call(Name(id="eval", ctx=Load()), args=[Call(Name(id="input", ctx=Load()), args=[], keywords=[])], keywords=[]))],
    #     type_ignores = []
    # )

    # tree = Module(
    #     body = [Expr(BinOp(left=BinOp(left=Constant(1), op=Add(), right=Constant(1)), op=Add(), right=BinOp(left=Constant(1), op=Add(), right=Constant(1))))],
    #     type_ignores = []
    # )

    # tree = Module(
    #     body = [],
    #     type_ignores = []
    # )

    # tree = Module(
    #     body = [Expr()]
    #     type_ignores = []
    # )

    # prog = """(1+(1+2))+(3+4)
    # \n1
    # \n1"""

    # prog = """eval(input())"""

    prog = """1 + eval(input())"""


    dumper = ASTDump()
    print(dumper.dump(tree))

    
    
    #print(tree)
    print("\n====FROM AST.dump=====\n")
    tree = ast.parse(prog)
    print(ast.dump(tree, indent=4))