import re
import ast
from ast import *

# Token types
TOKEN_INT = 'INT'
TOKEN_PLUS = 'PLUS'
TOKEN_MINUS = 'MINUS'
TOKEN_LPAREN = 'LPAREN'
TOKEN_RPAREN = 'RPAREN'
TOKEN_PRINT = 'PRINT'
TOKEN_EOF = 'EOF'

# Tokenizer
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = self.tokenize()
        self.current_token_index = 0
    
    def tokenize(self):
        token_spec = [
            (r'\d+', TOKEN_INT),
            (r'\+', TOKEN_PLUS),
            (r'-', TOKEN_MINUS),
            (r'\(', TOKEN_LPAREN),
            (r'\)', TOKEN_RPAREN),
            (r'print', TOKEN_PRINT),
            (r'\s+', None)  # Ignore whitespace
        ]
        tokens = []
        while self.pos < len(self.text):
            match = None
            for pattern, tag in token_spec:
                regex = re.compile(pattern)
                match = regex.match(self.text, self.pos)
                if match:
                    if tag:
                        tokens.append((tag, match.group(0)))
                    self.pos = match.end()
                    break
            if not match:
                raise SyntaxError(f'Unexpected character: {self.text[self.pos]}')
        tokens.append((TOKEN_EOF, None))
        return tokens
    
    def get_next_token(self):
        token = self.tokens[self.current_token_index]
        self.current_token_index += 1
        return token

# AST Nodes
class AST:
    pass

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Num(AST):
    def __init__(self, value):
        self.value = value

class Print(AST):
    def __init__(self, expr):
        self.expr = expr

# Parser
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def eat(self, token_type):
        if self.current_token[0] == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise SyntaxError(f'Unexpected token: {self.current_token}')
    
    def factor(self):
        token = self.current_token
        if token[0] == TOKEN_INT:
            self.eat(TOKEN_INT)
            return Num(int(token[1]))
        elif token[0] == TOKEN_MINUS:
            self.eat(TOKEN_MINUS)
            return UnaryOp('-', self.factor())
        elif token[0] == TOKEN_LPAREN:
            self.eat(TOKEN_LPAREN)
            node = self.expr()
            self.eat(TOKEN_RPAREN)
            return node
        else:
            raise SyntaxError(f'Unexpected token: {token}')
    
    def term(self):
        return self.factor()
    
    def expr(self):
        node = self.term()
        while self.current_token[0] == TOKEN_PLUS:
            token = self.current_token
            self.eat(TOKEN_PLUS)
            node = BinOp(left=node, op='+', right=self.term())
        return node
    
    def statement(self):
        if self.current_token[0] == TOKEN_PRINT:
            self.eat(TOKEN_PRINT)
            self.eat(TOKEN_LPAREN)
            node = Print(self.expr())
            self.eat(TOKEN_RPAREN)
            return node
        else:
            return self.expr()
    
    def parse(self):
        return self.statement()

# AST Printer
class ASTPrinter:
    def visit(self, node, depth=0):
        indent = '  ' * depth
        if isinstance(node, Num):
            print(f'{indent}Num({node.value})')
        elif isinstance(node, UnaryOp):
            print(f'{indent}UnaryOp({node.op})')
            self.visit(node.expr, depth + 1)
        elif isinstance(node, BinOp):
            print(f'{indent}BinOp({node.op})')
            self.visit(node.left, depth + 1)
            self.visit(node.right, depth + 1)
        elif isinstance(node, Print):
            print(f'{indent}Print')
            self.visit(node.expr, depth + 1)

# Example usage
if __name__ == '__main__':

    prog = """1 + -(2 + (3 + 4))"""
    
    lexer = Lexer(prog)
    print(f"TOKENS : {lexer.tokens}")
    
    parser = Parser(lexer)
    ast = parser.parse()


    printer = ASTPrinter()
    printer.visit(ast)
