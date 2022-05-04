import sys

ll=[]
# 入力
for line in sys.stdin.readlines():
    A=list(map(str, line.split(',')))
    ll.append(A)

# count
l_out=[]
for l in ll:
    PLAYER=l[0]
    W_NUM=l[1:].count('W')
    L_NUM=l[1:].count('L')
    D_NUM=l[1:].count('D')
    l_out.append([PLAYER,W_NUM,L_NUM,D_NUM])

# sort
l_out.sort(key=lambda val: val[3], reverse=True)
l_out.sort(key=lambda val: val[2], reverse=True)
l_out.sort(key=lambda val: val[1], reverse=True)

print("Player,W,L,D")
for l in l_out:
    print(*l, sep=',')
