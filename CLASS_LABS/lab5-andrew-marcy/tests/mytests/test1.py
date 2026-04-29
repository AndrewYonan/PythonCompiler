# EXAMPLES

a = 1
def f(a,b):
    return a


a = 1
def f(a,b):
    a = 2
    return a


a = 1
b = 3
def f(a,b):
    return lambda x : x + a + b
b = 17
print(f(1,2)(6))