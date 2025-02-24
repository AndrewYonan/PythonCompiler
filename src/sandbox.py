import ast
from ast import *

node =ast.USub()
node = ast.Add()
node = ast.Name(id="x", ctx=Load())  
node = ast.Name(id="x", ctx=ast.Load())  
node = ast.Name(id="x", ctx=ast.Store)   
node = ast.Name(id="x", ctx=ast.Del)     
