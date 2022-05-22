def comb(n, r):
    num = 1
    den = 1
    for i in range(r):
        num *= (n - i)
        den *= (r - i)
    return num // den

print(comb(5, 1)) # 5C1   5
print(comb(5, 2)) # 5C2   10
print(comb(5, 3)) # 5C3   10
print(comb(5, 4)) # 5C4   5
print(comb(5, 5)) # 5C5   1
print(comb(1, 5)) # error 0
print(comb(2, 5)) # error 0
print(comb(3, 5)) # error 0
print(comb(4, 5)) # error 0
print(comb(5, 5)) # 5C5   1

