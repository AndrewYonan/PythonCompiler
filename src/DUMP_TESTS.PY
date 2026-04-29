# tree = Module(
    #     body = [Expr(value=BinOp(left=BinOp(left=Constant(1), op=Add(), right=BinOp(left=Constant(1), op=Add(), right=Constant(2))), op=Add(), right=BinOp(left=Constant(3), op=Add(), right=Constant(4)))),
    #             Expr(value=Constant(1)),
    #             Expr(value=Constant(1)),
    #             Expr(BinOp(left=Constant(112), op=Add(), right=Call(Name(id="eval", ctx=Load()), args=[Call(Name(id="input", ctx=Load()), args=[], keywords=[])], keywords=[])))],
    #     type_ignores = []
    # )

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

    # prog = """(1+(1+2))+(3+4)
    # \n1
    # \n1"""

    # prog = """-eval(input())"""

    # prog = """eval(input())"""

    # prog = """x = 1""

    # prog = """y=1
    # \nprint(1,y,1+1)""" 

    # tree = Module(
    #     body=[Expr(value=UnaryOp(op=USub(), operand=Call(Name(id="eval", ctx=Load()), args=[Call(Name(id="input", ctx=Load()), args=[], keywords=[])], keywords=[])))],
    #     type_ignores=[]
    # )

    # tree = Module(
    #     body=[Assign(targets=[Name(id="y", ctx=Store())], value=Constant(1)),
    #         Expr(Call(func=Name(id="print", ctx=Load()), args=[Constant(1), Name(id="y", ctx=Load()), BinOp(right=Constant(1), op=Add(), left=Constant(1))], keywords=[]))],
    #     type_ignores=[]
    # )

    # tree = Module(
    #     body=[Assign(targets=[Name(id="x", ctx=Store())], value=Constant(1)),
    #           Assign(targets=[Name(id="x", ctx=Store())], value=Constant(1)),
    #           Assign(targets=[Name(id="x", ctx=Store())], value=Constant(1)),
    #           Assign(targets=[Name(id="x", ctx=Store())], value=Constant(1))],
    #     type_ignores=[]
    # )



# tree = Module(
#         body = [Expr(
#             value=Call(
#                 func=Name(id="print", ctx=Load()), 
#                 args=BinOp(left=Constant(1), op=Add(), right=Constant(3)), 
#                 keywords=[]))],
#         type_ignores = []
#     )








#USAGE



    # dumper = ASTDump()
    # print(dumper.dump(tree))





# GOOD DUMP unit test

# prog = """y=1
#     \nprint(1,y,1+1)""" 

#     tree = Module(
#         body=[Assign(targets=[Name(id="y", ctx=Store())], value=Constant(1)),
#             Expr(Call(func=Name(id="print", ctx=Load()), args=[Constant(1), Name(id="y", ctx=Load()), BinOp(right=Constant(1), op=Add(), left=Constant(1))], keywords=[]))],
#         type_ignores=[]
#     )

#     dumper = ASTDump()
#     print(dumper.dump(tree))
#     print()
    

#     print("\n====FROM AST.dump=====\n")
#     tree = ast.parse(prog)
#     print(ast.dump(tree, indent=4))