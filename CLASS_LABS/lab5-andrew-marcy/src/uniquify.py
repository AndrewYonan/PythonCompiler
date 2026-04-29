from flatten import *


def to_atomic_str(node):
    if isinstance(node, ast.Constant):
        return str(node.value)
    elif isinstance(node, ast.Name):
        return node.id
    else:
        print(f"ERR : to_atomic_str({node})")
        exit(1)


class UniquifyAST():

    def __init__(self):
        self.counter = 0

    def uniquify(self, node, env=[]):        

        if isinstance(node, ast.Module):

            body_suite = []

            for child_node in node.body:
                body_suite.append(self.uniquify(child_node, env))
            
            return ast.Module(
                body = body_suite,
                type_ignores = []
            )
        
        elif isinstance(node, ast.FunctionDef):

            for arg in node.args.args:
                if arg in env:
                print(f" arg = {arg.arg}")
            exit(1)
        
        else:
            return node




def uniquify(tree):
    return UniquifyAST().uniquify(tree)




if __name__ == "__main__":

    if (len(sys.argv) < 2):
        print("Usage : python3 flatten_tester.py <python prog>")
        exit(1)

    file = sys.argv[1]

    if not os.path.exists(file):
        print(f"filed '{file}' could not be opened")
        sys.exit(1)
    
    with open(file, 'r') as f:
        prog = f.read()
    
    print("========PROG========")
    print(prog)

    py_ast = ast.parse(prog)

    print("====AST PROG=====")
    print(ast.dump(py_ast, indent=4))

    
    py_ast = uniquify(py_ast)
    print("====Uniqufied PROG=====")
    print(un_parse(py_ast))


    # py_ast = rename_source_variables(py_ast)
    
    # print("====unparsed result======")
    # print(un_parse(py_ast))

    # flat_tree = flatten(py_ast)
    # print("====FLAT PROG======")
    # print(un_parse(flat_tree))