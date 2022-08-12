from qreki import Kyureki
from datetime import date
from collections import defaultdict
dict = defaultdict(list)

#k = Kyureki.from_ymd(2022, 5, 5)
#k_str=str(k)
#print(k.rokuyou)

print("---")
for yy in range(1980, 2101):
    year=yy
    month=5
    day=5
    d = date(year, month, day)
    k = Kyureki.from_date(d)

    string = str(year) + str(month).zfill(2) + str(day).zfill(2)
    dict[int(string)].append(k.rokuyou)
    #print(k.rokuyou)
    print('{}, {}'.format(string, k.rokuyou))

print("--- 仏滅")
for k in dict:
    #print(dict[k][0])
    if dict[k][0] == '仏滅':
        print('{}, {}'.format(k, dict[k][0]))
