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



a = 1
b = 0
def f(a,b):
    a = 42
    print(b)
    return lambda a : a + a
b = 10
print(f(1,2)(17))




a = 1
b = 0
def f(a,b):
    a = 42
    print(b)
    return lambda a : lambda a : a + a
b = 10

print(f(1,2)(17)(2))


a = 1
z = 10
def makePlusK(k, a):
    z = -100
    return lambda y : y + k + a + z

print(makePlusK(5, -50000)(10))