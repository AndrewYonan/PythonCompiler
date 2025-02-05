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

class Store:
    def __repr__(self):
        return "Store()"
    



# DUMP METHOD (for testing)
# =============================================

def takes_single_line(str):
    return "\n" not in str


class ASTDump:
    
    def __init__(self):
        self.indent = " "*3
    
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

            dump_str = "["

            if len(node) == 0:
                return str(node) 
            
            s1 = self.indent * (depth + 1)
            
            for i in range(len(node)):

                comma = "" if i == len(node) - 1 else ","
                
                str_elem = self.dump(node[i], depth + 1)
                nline = "\n"
                dump_str += f"{nline}{s1}{str_elem}{comma}" 
            
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
        
        if isinstance(node, UnaryOp):
            s1 = self.indent * depth
            s2 = self.indent * (depth + 1)
            operand = self.dump(node.operand, depth+1)
            return f"UnaryOp(\n{s2}op={node.op},\n{s2}operand={operand})"
        
        if isinstance(node, Call):
            s1 = self.indent * depth
            s2 = self.indent * (depth + 1)
            args = self.dump(node.args, depth + 1)
            return f"Call(\n{s2}func={node.func},\n{s2}args={args}{s2}\n{s2}keywords={node.keywords})"
    
        if isinstance(node, Assign):
            s1 = self.indent * depth
            s2 = self.indent * (depth + 1)
            targets = self.dump(node.targets, depth + 1)
            value = self.dump(node.value, depth + 1)
            return f"Assign(\n{s2}targets={targets}\n{s2}value={value})" 
        
        if isinstance(node, Name):
            s1 = self.indent * depth
            s2 = self.indent * (depth + 1)
            return f"{node}"



if __name__ == "__main__":
    pass