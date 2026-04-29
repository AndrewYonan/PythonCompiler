#!/usr/bin/env python3.10

import ast
from ast import *

class RenameVariables(ast.NodeTransformer):
    def visit(self, node):
        self.generic_visit(node)
        if isinstance(node, ast.Name):
            if (node.id != "print" 
                and node.id != "eval"
                and node.id != "input"):
                    return ast.Name(
                        id = "s_" + node.id, 
                        ctx = node.ctx)
        return node




#replace module's body with this new flattened body
class FlattenAST(ast.NodeTransformer):
    counter = 0
    new_body = []
    def visit_Module(self, node):
        #visit the children first
        self.generic_visit(node)
        #replace body with new body
        return ast.Module(
            body = self.new_body,
            type_ignores = node.type_ignores
        )
    def visit_Expr(self, node):
        self.generic_visit(node)
        self.new_body.append(node)
    def visit_Assign(self, node):
        self.generic_visit(node)
        #assuming that visitng the children has flattened them already
        self.new_body.append(node)
    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if (isinstance(node.operand, Call)):
            self.new_body.append(ast.Assign(
                targets = [ast.Name(id = ("temp" + str(self.counter)), ctx = ast.Store())],
                value = node.operand
            ))
            self.counter = self.counter + 1
            return ast.UnaryOp(
                op = ast.USub(),
                operand = ast.Name(id = ("temp" + str(self.counter - 1)), ctx = ast.Load())
            )
        elif (isinstance(node.operand, BinOp)):
            self.new_body.append(ast.Assign(
                targets = [ast.Name(id = ("temp" + str(self.counter)), ctx = ast.Store())],
                value = node.operand
            ))
            self.counter = self.counter + 1
            return ast.UnaryOp(
                op = ast.USub(),
                operand = ast.Name(id = ("temp" + str(self.counter - 1)), cts = ast.Load())
            )
        else:
            self.new_body.append(ast.Assign(
                targets = [ast.Name(id = ("temp" + str(self.counter)), cts = ast.Store())],
                value = ast.UnaryOp(
                    op = ast.USub(),
                    operand = node.operand
                )))
            self.counter = self.counter + 1
            return ast.Name(id = ("temp" + str(self.counter - 1)), cts = ast.Load())
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if (isinstance(node.left, BinOp)):
            self.new_body.append(ast.Assign(
                targets = [ast.Name(id = ("temp" + str(self.counter)), ctx = ast.Store())],
                value = node.left
            ))
            self.counter = self.counter + 1
            return ast.BinOp(
                left = ast.Name(id = ("temp" + str(self.counter - 1)), ctx = ast.Load()),
                op = node.op,
                right = node.right
            )
        elif (isinstance(node.left, UnaryOp)):
            self.new_body.append(ast.Assign(
                targets = [ast.Name(id = ("temp" + str(self.counter)), ctx = ast.Store())],
                value = ast.UnaryOp(op = ast.USub(), operand = node.left.operand)
            ))
            self.counter = self.counter + 1
            return ast.BinOp(
                left = ast.Name(id = ("temp" + str(self.counter - 1)), ctx = ast.Load()),
                op = node.op,
                right = node.right
            )
        elif (isinstance(node.right, BinOp)):
            self.new_body.append(ast.Assign(
                targets = [ast.Name(id = ("temp" + str(self.counter)), ctx = ast.Store())],
                value = node.right
            ))
            self.counter = self.counter + 1
            return ast.BinOp(
                left = node.left,
                op = node.op,
                right = ast.Name(id = ("temp" + str(self.counter - 1)), ctx = ast.Load())
            )
        elif (isinstance(node.right, UnaryOp)):
            self.new_body.append(ast.Assign(
                targets = [ast.Name(id = ("temp" + str(self.counter)), ctx = ast.Store())],
                value = ast.UnaryOp(op = ast.USub(), operand = node.right.operand)
            ))
            self.counter = self.counter + 1
            return ast.BinOp(
                left = node.left,
                op = node.op,
                right = ast.Name(id = ("temp" + str(self.counter - 1)), ctx = ast.Load())
            )
        else:
            self.new_body.append(ast.Assign(
                targets = [ast.Name(id = ("temp" + str(self.counter)), ctx = ast.Store())],
                value = node
            ))
            self.counter = self.counter + 1
            return ast.Name(id = ("temp" + str(self.counter - 1)), ctx = ast.Load())
    def visit_Call(self, node):
        self.generic_visit(node)
        if (node.func.id == "print" and isinstance(node.args[0], BinOp)):
            self.new_body.append(ast.Assign(
                targets = [ast.Name(id = ("temp" + str(self.counter)), ctx = ast.Store())],
                value = node.args[0]
            ))
            self.counter = self.counter + 1
            self.new_body.append(ast.Call(
                func = node.func,
                args = [ast.Name(id = ("temp" + str(self.counter - 1)), ctx = ast.Load())],
                keywords = node.keywords
            ))
        elif (node.func.id == "eval"):
            self.new_body.append(ast.Assign(
                targets = [ast.Name(id = ("temp" + str(self.counter)), ctx = ast.Store())],
                value = node
            ))
            self.counter = self.counter + 1
            return ast.Name(id = ("temp" + str(self.counter - 1)), ctx = ast.Load())
        else:
            return node
                



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
    



def process_p0_prog(prog):

    print(f"====P0-PROG====:\n {prog}\n")

    unparser = UnParser()

    tree = ast.parse(prog)
    renamed_tree = RenameVariables().visit(tree)

    print(f"====RENAMED P0-PROG====:")
    print(unparser.un_parse(renamed_tree))

    flat_tree = FlattenAST().visit(renamed_tree)

    print("===FLATTENED P0-PROG===")
    print(unparser.un_parse(flat_tree))



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
            

            