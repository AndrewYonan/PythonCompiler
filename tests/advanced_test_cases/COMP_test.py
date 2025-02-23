
print(eval(input()) if eval(input()) else eval(input()))
print(eval(input()))

i = 1
sum = 1

while int(i != 10):
    j = i
    while int(j != 10):
        j = j + 1
        sum = sum + j
    i = i + 1

print(sum)