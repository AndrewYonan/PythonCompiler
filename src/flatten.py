import ast
from ast import *


def get_ast(prog):
    return ast.parse(prog)



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



class RenameVariables(ast.NodeTransformer):
    def visit(self, node):
        self.generic_visit(node)
        if isinstance(node, ast.Name):
            if node.id != "print" and node.id != "eval" and node.id != "input":
                return ast.Name(
                    id = "s_" + node.id,
                    ctx = node.ctx
                )
        return node



def is_simple_BinOp(node):
    if isinstance(node, ast.BinOp):
        return (isinstance(node.left, ast.Constant) or isinstance(node.left, ast.Name)) and (isinstance(node.right, ast.Constant) or (isinstance(node.right, ast.Name)))
    return False



def is_simple_UnaryOp(node):
    if isinstance(node, ast.UnaryOp):
        return isinstance(node.operand, ast.Constant) or isinstance(node.operand, ast.Name)
    return False



def is_simple_Expr(node):
    return isinstance(node, ast.Constant) or is_simple_BinOp(node) or is_simple_UnaryOp(node)



def is_simple_statement(node):

    if isinstance(node, ast.Assign):
        return is_simple_Expr(node.value)
    
    if isinstance(node, ast.BinOp):
        return is_simple_BinOp(node)
    
    if isinstance(node, ast.UnaryOp):
        return is_simple_UnaryOp(node)

    if isinstance(node, ast.Expr):
        return is_simple_BinOp(node) or is_simple_UnaryOp(node)
    
    if isinstance(node, ast.Constant):
        return True
    
    if isinstance(node, ast.Name):
        if node.id != "print" and node.id != "eval":
            return True


def is_atomic(node):
    if isinstance(node, ast.Constant):
        return True
    elif isinstance(node, ast.Name):
        if node.id != "eval" and node.id != "input":
            return True



def is_eval_input(node):
    if isinstance(node, ast.Call):
        if node.func.id == "eval":
            if node.args[0].func.id == "input":
                return True

def temp_name_node(temp_id):
    return ast.Name(id = temp_id, ctx = Load())

def new_assign_node(node, temp_id):
    if is_simple_BinOp(node) or is_simple_UnaryOp(node) or is_eval_input(node):
        return ast.Assign(targets = [Name(id = temp_id, ctx = Store())],
                          value = node)
    else:
        print(f"in new_assign_node, node {node} is NOT A SIMPLE BIN_OP or UNARY_OP or Eval_input")



class FlattenAST():

    def __init__(self):

        self.counter = 0 
        self.flattened_body = [] 

    def flatten(self, node):

        if isinstance(node, ast.Module):

            for child_node in ast.iter_child_nodes(node):
                self.flatten(child_node)
                self.flattened_body.append(child_node)

        elif is_simple_statement(node):
            return


        elif isinstance(node, ast.Assign):
            self.flatten(node.value)


        elif isinstance(node, ast.Expr):
            self.flatten(node.value)


        elif isinstance(node, ast.BinOp):

            self.flatten(node.left)
            
            if not is_atomic(node.left):

                id = self.add_temp_assign_node(node.left)
                node.left = temp_name_node(id)
                
            self.flatten(node.right)

            if not is_atomic(node.right):

                id = self.add_temp_assign_node(node.right)
                node.right = temp_name_node(id)
        
        elif isinstance(node, ast.UnaryOp):

            self.flatten(node.operand)

            if not is_atomic(node.operand):

                id = self.add_temp_assign_node(node.operand)
                node.operand = temp_name_node(id)
                

        elif isinstance(node, ast.Call):

            if is_eval_input(node):
                return

            for i, arg in enumerate(node.args):
                self.flatten(arg)

                if not is_atomic(arg):

                    id = self.add_temp_assign_node(arg)
                    node.args[i] = temp_name_node(id)


    def add_temp_assign_node(self, node):

        id = f"temp_{self.counter}"
        self.counter = self.counter + 1
        self.flattened_body.append(new_assign_node(node, id))
        return id



        

    

def flatten_ast(tree):

    flattener = FlattenAST()
    flattener.flatten(tree)

    return ast.Module(
        body = flattener.flattened_body,
        type_ignores = tree.type_ignores
    )





# tree = get_ast(prog)
# renamed_tree = RenameVariables().visit(tree)

# print(f"\nProg : {prog}")
# print(f"\nProg tree: {ast.dump(tree, indent=3)}")
# print(f"\nRenamed Prog :\n{UnParser().un_parse(renamed_tree)}")

# flat_tree = flatten_ast(tree)

# print(f"\nFlattened Prog Tree :\n{ast.dump(flat_tree, indent=2)}")
# print(f"\nFlattened Prog :\n{UnParser().un_parse(flat_tree)}")
