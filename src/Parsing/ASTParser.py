import re 
import ast
from ast import *
from ASTClasses import *
from ASTDump import *


TOKEN_INT = "INT"
TOKEN_PLUS = "PLUS"
TOKEN_MINUS = "MINUS"
TOKEN_VAR = "VAR"
TOKEN_EQUAL = "EQUAL"
TOKEN_LPAREN = "LPAREN"
TOKEN_RPAREN = "RPAREN"
TOKEN_PRINT = "PRINT"
TOKEN_EVAL_INPUT = "EVAL_INPUT"
TOKEN_NEWLINE =  "NEWLINE"
TOKEN_EOF = "EOF"


token_spec = [(r'print', TOKEN_PRINT),
              (r'eval\(\s*input\(\)\s*\)', TOKEN_EVAL_INPUT),
              (r'[a-zA-Z_][a-zA-Z0-9_]*', TOKEN_VAR),
              (r'\d+', TOKEN_INT),
              (r'\+', TOKEN_PLUS),
              (r'\-', TOKEN_MINUS),
              (r'=', TOKEN_EQUAL),
              (r'\(', TOKEN_LPAREN),
              (r'\)', TOKEN_RPAREN),
              (r'\n', TOKEN_NEWLINE),
              (r'\s+', None)] # to ignore whitespace



class Lexer:

    def __init__(self, text):
        self.text = text
        self.tokens = self.tokenize()
        self.token_idx = 0
        self.is_empty = False

    def tokenize(self):
        tokens = []
        pos = 0
        while pos < len(self.text):
            match = None
            for pattern, tag in token_spec:
                regex = re.compile(pattern)
                match = regex.match(self.text, pos)
                if match:
                    if tag:
                        tokens.append((tag, match.group(0)))
                    pos = match.end()
                    break
            if not match:
                print(f'ERR : unexpected character: {self.text[pos]}')
                return
        tokens.append((TOKEN_EOF, None))
        return tokens
    
    def get_next_token(self):
        if self.token_idx == len(self.tokens):
            self.is_empty = True
            return None
        token = self.tokens[self.token_idx]
        self.token_idx += 1
        return token

    def empty(self):
        return self.is_empty



class Parser:

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.module_body = []

    def at_prog_end(self):
        return self.current_token[0] == TOKEN_EOF
    
    def consume(self, token_type):
        if self.current_token[0] == token_type:
            self.current_token = self.lexer.get_next_token()
            # print(f"[+] parser consumed token {token_type}")
        else:
            print(f"ERR : unexpected token {self.current_token}")
            exit(1)
    
    def strip_newlines(self):
        while self.current_token[0] == TOKEN_NEWLINE:
            self.consume(TOKEN_NEWLINE)
    
    def factor(self):
        token = self.current_token
        if token[0] == TOKEN_INT:
            self.consume(TOKEN_INT)
            return Constant(value=int(token[1]))
        if token[0] == TOKEN_LPAREN:
            self.consume(TOKEN_LPAREN)
            node = self.expr()
            self.consume(TOKEN_RPAREN)
            return node
    
    def term(self):
        return self.factor()
    
    def expr(self):
        node = self.term()
        while self.current_token[0] == TOKEN_PLUS:
            token = self.current_token
            self.consume(TOKEN_PLUS)
            node = BinOp(left = node,
                        op = Add(),
                        right = self.term())
        return node
    
    def simple_statement(self):
        if self.current_token[0] == TOKEN_PRINT:
            self.consume(TOKEN_PRINT)
            self.consume(TOKEN_LPAREN)
            node = Call(func=Name(id="print", ctx=Load()),
                        args=[self.expr()],
                        keywords=[])
            self.consume(TOKEN_RPAREN)
            return Expr(value=node)
        
        else:
            return Expr(value = self.expr())
    
    def get_next_statement(self):
        self.strip_newlines()
        if self.at_prog_end():
            return None
        return self.simple_statement()

    def parse(self):

        self.strip_newlines()

        while not self.at_prog_end():
            statement = self.get_next_statement()
            if statement:
                self.module_body.append(statement)

        return Module(
            body = self.module_body,
            type_ignores=[]
        )



if __name__ == "__main__":

    prog = """(((1)))"""

    lex = Lexer(prog)
    lex.tokenize()

    print("=====prog TOKENS=====")

    print(f"{lex.tokens}")

    print(f"from astParse:\n {ast.dump(ast.parse(prog), indent=3)}")

    print("=====Parse results======")

    parser = Parser(lex)
    tree = parser.parse()

    dumper = ASTDump()
    print(dumper.dump(tree))