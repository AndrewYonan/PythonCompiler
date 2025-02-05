import re 
import ast
from ast import *
from ASTClasses import *

TOKEN_INT = "INT"
TOKEN_PLUS = "PLUS"
TOKEN_MINUS = "MINUS"
TOKEN_VAR = "VAR"
TOKEN_EQUAL = "EQUAL"
TOKEN_LPAREN = "LPAREN"
TOKEN_RPAREN = "RPAREN"
TOKEN_PRINT = "PRINT"
TOKEN_EVAL_INPUT = "EVAL_INPUT"
TOKEN_EOF = "EOF"


token_spec = [(r'print', TOKEN_PRINT),
              (r'eval\(\s*input\(\)\s*\)', TOKEN_EVAL_INPUT),
              (r'\d+', TOKEN_INT),
              (r'\+', TOKEN_PLUS),
              (r'\-', TOKEN_MINUS),
              (r'[a-zA-Z_][a-zA-Z0-9_]*', TOKEN_VAR),
              (r'=', TOKEN_EQUAL),
              (r'\(', TOKEN_LPAREN),
              (r'\)', TOKEN_RPAREN),
              (r'\s+', None)]



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
    




if __name__ == "__main__":

    prog = """x=1
    y=2
    print(1-(x + y + eval(input)))"""

    lex = Lexer(prog)
    lex.tokenize()

    while lex.empty() == False:
        print(lex.get_next_token())
    
    pass