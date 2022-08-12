from collections import Counter

l = ['a', 'a', 'a', 'a', 'b', 'c', 'c']
c = Counter(l)
print(c)
print(c['a'])
print(c['b'])
print(c['c'])
print(c.values())
for i in c.values():
    print(i)

d = Counter([1, 3, 5, 6, 8])
print(d.values())
for i in d.values():
    print(i)

#Counter({'a': 4, 'c': 2, 'b': 1})
#4
#1
#2
#dict_values([4, 1, 2])
#4
#1
#2
