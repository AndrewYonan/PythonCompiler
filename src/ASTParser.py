import sys
import os
import re 
import ast
from ast import *
from ASTClasses import *
from ASTDump import *

TOKEN_INT = "INT"
TOKEN_PLUS = "PLUS"
TOKEN_MINUS = "MINUS"
TOKEN_VAR = "VAR"
TOKEN_ASSIGN = "ASSIGN"
TOKEN_LPAREN = "LPAREN"
TOKEN_RPAREN = "RPAREN"
TOKEN_PRINT = "PRINT"
TOKEN_EVAL_INPUT = "EVAL_INPUT"
TOKEN_NEWLINE =  "NEWLINE"
TOKEN_COMMENT = "#"
TOKEN_WHITESPACE = "WHITESPACE"
TOKEN_EOF = "EOF"

# p0a additions:
TOKEN_IF = "IF"
TOKEN_WHILE = "WHILE"
TOKEN_EQ = "EQ"
TOKEN_NEQ = "NEQ"
TOKEN_INT_BCAST = "INT_BCAST"
TOKEN_NOT = "NOT"
TOKEN_AND = "AND"
TOKEN_OR = "OR"
TOKEN_COLON = "COLON"
TOKEN_INDENT = "INDENT"
TOKEN_DEDENT = "DEDENT"

token_spec = [(r'print', TOKEN_PRINT),
              (r'eval\(\s*input\(\)\s*\)', TOKEN_EVAL_INPUT),
              (r'if', TOKEN_IF),
              (r'while', TOKEN_WHILE),
              (r'!=', TOKEN_NEQ),
              (r'int', TOKEN_INT_BCAST),
              (r'not', TOKEN_NOT),
              (r'and', TOKEN_AND),
              (r'or', TOKEN_OR),
              (r'\d+', TOKEN_INT),
              (r'\+', TOKEN_PLUS),
              (r'\-', TOKEN_MINUS),
              (r'==', TOKEN_EQ),
              (r'=', TOKEN_ASSIGN),
              (r'\(', TOKEN_LPAREN),
              (r'\)', TOKEN_RPAREN),
              (r':', TOKEN_COLON),
              (r'(\n\s*)(\n|\Z)', TOKEN_NEWLINE),
              (r'\n(\s*)[^\n]', TOKEN_INDENT),
              (r'[a-zA-Z_][a-zA-Z0-9_]*', TOKEN_VAR),
              (r'#.*(\n|\Z)', TOKEN_COMMENT),
              (r'\s+', TOKEN_WHITESPACE)] 



def assert_proper_indent(indent, location):
    if (indent % 4 != 0):
        print(f"Parse Err : unexpected indent size : {indent} at {location}")
        exit(1)


class Lexer:

    def __init__(self, text):
        self.text = text
        self.tokens = self.tokenize()
        self.token_idx = 0
        self.is_empty = False

    def tokenize(self):

        tokens = []
        pos = 0

        prev_indent = 0
        cur_indent = 0

        while pos < len(self.text):

            match = None

            for pattern, tag in token_spec:

                regex = re.compile(pattern)
                match = regex.match(self.text, pos)

                if match:

                    if tag == TOKEN_NEWLINE:
                        end = match.end(1)

                    elif tag != TOKEN_WHITESPACE and tag != TOKEN_COMMENT:

                        if tag == TOKEN_INDENT:

                            cur_indent = len(match.group(1))
                            assert_proper_indent(cur_indent, match.group(0))

                            if (cur_indent > prev_indent):
                                tokens.append((TOKEN_INDENT, None))
                                prev_indent = cur_indent
                            
                            elif (cur_indent < prev_indent):
                                for _ in range((prev_indent - cur_indent) // 4):
                                    tokens.append((TOKEN_DEDENT, None))
                                prev_indent = cur_indent
                            
                            prev_indent = cur_indent
                            end = match.end(1)
                        
                        else:
                            tokens.append((tag, match.group(0)))
                            end = match.end()
                    else:
                        end = match.end()
                    
                    pos = end

                    break

            if not match:
                print(f'ERR : unmatched character: {self.text[pos]}')
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

    def look_ahead(self):
        if self.token_idx >= len(self.tokens) - 1:
            return None
        return self.tokens[self.token_idx]

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
            return Constant(value = int(token[1]))

        if token[0] == TOKEN_MINUS:
            self.consume(TOKEN_MINUS)
            return UnaryOp(op = USub(), operand=self.term())

        if token[0] == TOKEN_LPAREN:
            self.consume(TOKEN_LPAREN)
            node = self.expr()
            self.consume(TOKEN_RPAREN)
            return node
        
        if token[0] == TOKEN_VAR:
            self.consume(TOKEN_VAR)
            return Name(id = token[1], ctx = Load())
        
        if token[0] == TOKEN_EVAL_INPUT:
            self.consume(TOKEN_EVAL_INPUT)
            return Call(func = Name(id = "eval", ctx = Load()), 
                                    args = [
                                        Call(func = Name(id = "input", ctx = Load()),
                                            args = [],
                                            keywords = [])], 
                                    keywords = [])
    
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
        
        if self.current_token[0] == TOKEN_VAR:
            next_token = self.lexer.look_ahead()
            if next_token:
                if next_token[0] == TOKEN_ASSIGN:
                    id_var = self.current_token[1]
                    self.consume(TOKEN_VAR)
                    self.consume(TOKEN_ASSIGN)
                    return Assign(targets = [Name(id = id_var, ctx = Store())], value = self.expr())

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

    if (len(sys.argv) < 2):
        print("Usage : python3 ASTParser.py <python test program>")
        exit(1)

    prog_file = sys.argv[1]

    if not os.path.exists(prog_file):
        print(f"file '{prog_file}' could not be opened")
        sys.exit(1)

    with open(prog_file, 'r') as file:
        prog = file.read()


    print(f"=======P0 Prog=======")
    print(prog)
    lex = Lexer(prog)

    print("=====prog TOKENS=====")
    tokens = lex.tokens
    for i in range(len(tokens)):
        if (i+1) % 4 == 0:
            print(tokens[i])
        else:
            print(tokens[i], end="")
    print()
    # print(f"from astParse:\n {ast.dump(ast.parse(prog), indent=3)}")

    print("=====Parse results======")

    # parser = Parser(lex)
    # tree = parser.parse()
    
    # dumper = ASTDump()
    # print(dumper.dump(tree))