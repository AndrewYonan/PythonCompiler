import ast
from ast import *
from ASTClasses import *


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
    
    prog = """y=1
    \nprint(1,y,1+1)""" 

    print("\n====FROM custom dump method:=====\n")

    tree = Module(
        body=[Assign(targets=[Name(id="y", ctx=Store())], value=Constant(1)),
            Expr(Call(func=Name(id="print", ctx=Load()), args=[Constant(1), Name(id="y", ctx=Load()), BinOp(right=Constant(1), op=Add(), left=Constant(1))], keywords=[]))],
        type_ignores=[]
    )

    dumper = ASTDump()
    print(dumper.dump(tree))
    

    print("\n====FROM AST.dump=====\n")
    tree = ast.parse(prog)
    print(ast.dump(tree, indent=4))



