
# AST classes
# ===========================================

class Module:
    def __init__(self, body, type_ignores):
        self.body = body
        self.type_ignores = type_ignores
    def __repr__(self):
        return f"Module(body={self.body}, type_ignores={self.type_ignores})"

class Assign:
    def __init__(self, targets, value):
        self.targets = targets
        self.value = value
    def __repr(self):
        return f"Assign(targets={self.targets}, value={self.value})"

class Name:
    def __init__(self, id, ctx):
        self.id = id
        self.ctx = ctx
    def __repr__(self):
        return f"Name(id=\'{self.id}\', ctx={self.ctx})"

class Constant:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Constant(value={self.value})"

class Expr:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Expr(value={self.value})"

class Call:
    def __init__(self, func, args, keywords):
        self.func = func
        self.args = args
        self.keywords = keywords
    def __repr__(self):
        return f"Call(func={self.func}, args={self.args}, keywords={self.keywords})"

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return f"BinOp(left={self.left}, op={self.op}, right={self.right})"

class UnaryOp:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
    def __repr__(self):
        return f"UnaryOp(op={self.op}, operand={self.operand})"

class USub:
    def __repr__(self):
        return "USub()"

class Add:
    def __repr__(self):
        return "Add()"

class Load:
    def __repr__(self):
        return "Load()"

class Store:
    def __repr__(self):
        return "Store()"