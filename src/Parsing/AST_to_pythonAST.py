import ast
from ast import *
from ASTClasses import *
from ASTParser import *
from ASTDump import *


class CustomToPythonASTConverter():
    
    def __init__(self):
        self.module_body = []

    def convert(self, node):

        if isinstance(node, Module):
            return ast.Module(
                body = self.convert(node.body),
                type_ignores = []
            )
        
        if isinstance(node, list):
            new_list = []
            for elem in node:
                new_list.append(self.convert(elem))
            return new_list
        
        if isinstance(node, Assign):
            return ast.Assign(
                targets = self.convert(node.targets),
                value = self.convert(node.value)
            )

        if isinstance(node, Expr):
            return ast.Expr(value = self.convert(node.value))

        if isinstance(node, Name):
            return ast.Name(id = node.id, ctx = self.convert(node.ctx))
        
        if isinstance(node, Store):
            return ast.Store()
        
        if isinstance(node, Load):
            return ast.Load()

        if isinstance(node, BinOp):
            return ast.BinOp(
                left = self.convert(node.left),
                op = self.convert(node.op),
                right = self.convert(node.right)
            )
        if isinstance(node, UnaryOp):
            return ast.UnaryOp(
                op = self.convert(node.op),
                operand = self.convert(node.operand)
            )

        if isinstance(node, Add):
            return ast.Add()
        
        if isinstance(node, USub):
            return ast.USub()
        
        if isinstance(node, Constant):
            return ast.Constant()
        
        if isinstance(node, Call):
            return ast.Call(
                func = self.convert(node.func),
                args = self.convert(node.args),
                keywords = self.convert(node.keywords)
            )
        

                    

if __name__ == "__main__":

    prog = """x = -(--1 + eval(input()))
    \ny = 1
    \n1 + 1"""

    lexer = Lexer(prog)
    lexer.tokenize()

    print("======tokens=======")
    print(lexer.tokens)

    parser = Parser(lexer)
    tree = parser.parse()

    dumper = ASTDump()

    print("=====from custum dump method=====\n")
    print(dumper.dump(tree))

    print(f"from astParse:\n {ast.dump(ast.parse(prog), indent=3)}")

    converter = CustomToPythonASTConverter()

    new_tree = converter.convert(tree)
    print(ast.dump(new_tree, indent=2))






