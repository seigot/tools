import sys
import subprocess
import copy

# artの盤面を配列として取得する
# 取得した配列は逆順にして返す（後述する探索のため）
def receive_shapelist(n):
    shapelist = []
    for i in range(n):
        xi = str(input())
        shapelist.append(xi)
    shapelist.reverse()

    return shapelist

# found list (探索済みの場所を管理する配列) 初期化
# input
#   n: shapelistの行数
#   shapelist: 盤面の配列
# output
#   found list: 探索済みの場所を管理する配列
#               探索済みの場合はTrue, 未探索はFalse
def foundlist_init(n,shapelist):
    foundlist = [[False for i in range(10)] for i in range(n)]
    for i in range(n): # 各行
        for j in range(len(shapelist[i])): # 該当行の要素数
            # "0"の場合はTrue,それ以外はFalse
            foundlist[i][j] = True if shapelist[i][j] == "0" else False

    return foundlist

# 各行の未探索のxの位置を返す
# input
#   n: shapelistの行数
#   found list: 探索済みの場所を管理する配列
# output
#   x_with_block: 各行の未探索のxの位置
#                 (後述の探索結果の固定化を防ぐために順番をrandom()にする)
def x_with_block_init(n, foundlist):
    x_with_block = [[] for i in range(n)]
    for row in range(n):
        for x in range(len(foundlist[row])):
            if foundlist[row][x] == False:
                x_with_block[row].append(x)
        random.shuffle(x_with_block[row])

    return x_with_block

# Try other combinations of the x-coords if this key does not work.
# xs_0000 のケース用
# 上手く組み合わせを見つけられなかった場合は気を取り直して別の組み合わせがないか探す
def remove_if_deadend(key_order, foundlist, row, test_xs, x1,x2):
    if foundlist[row].count(False) != 0:
        key_order[row].remove(test_xs)
        foundlist[row][x1], foundlist[row][x2] = False, False

    return key_order, foundlist

# Try other combinations of the x-coords if this key does not work.
# xs_00_00 のケース用
# 上手く組み合わせを見つけられなかった場合は気を取り直して別の組み合わせがないか探す
def remove_if_deadend_2(key_order, foundlist, row, test_xs_xs, leftoverX, x3):
    if foundlist[row + 1].count(False) != 0:
        key_order[row].remove(test_xs_xs)
        foundlist[row][leftoverX], foundlist[row + 1][x3] = False, False

    return key_order, foundlist

# Implement bruteforce search to find key_order. Take 2 x-coords from x-with-block then check if procedure in artdict has been found.
# ブロックの組み合わせを再帰的に調べ上げる
# input
#   x_with_block: 各行,各列の探索対象ブロックの配列番号
#   key_order: 探索したブロックの組み合わせ
#   foundlist: 探索対象ブロックを管理する配列
#   row: 探索対象の行数
# output
#   key_order: 探索したブロックの組み合わせ(最終的に全探索したものを返す)  
def bruteforce(x_with_block, key_order, foundlist, row):
    if row == len(shapelist):
        # 全ての行を探索完了した場合は終了
        return key_order

    # Get two x-coords from x_with_block.
    # 全通りの組み合わせを探索する
    for t1 in range(len(x_with_block[row])):
        for t2 in range(t1+1,len(x_with_block[row])):
            x1 = min(x_with_block[row][t1],x_with_block[row][t2])
            x2 = max(x_with_block[row][t1],x_with_block[row][t2])
            # Convert the two x-coords into the key of artdict as test_xs 
            test_xs = "xs_"+ str(x1) + str(shapelist[row][x1]) + str(x2) + str(shapelist[row][x2])

            # Check if procedure in artdict has been found
            # Also, the x-coords must not already be in use. It may happen when the row before ended with xs_00_00. 
            # Update foundlist and key_order if the key is valid
            if lib.artdict[test_xs] != False and foundlist[row][x1] == False and foundlist[row][x2] == False:
                foundlist[row][x1], foundlist[row][x2] = True,True
                key_order[row].append(test_xs)

                # Move on to next row if all x-coords has been found 
                if foundlist[row].count(False) == 0:
                    key_order = bruteforce(x_with_block = x_with_block, key_order = key_order, foundlist=foundlist, row = row + 1)
                    # This might mean nothing                                       
                    key_order, foundlist = remove_if_deadend(key_order = key_order, foundlist = foundlist, row = row, test_xs = test_xs, x1 = x1, x2 = x2)

                # If only one x-coord has not been found, try combinations of the remaining x-coord and each x-coord in the next row
                # The key in this case is xs_00_00
                elif foundlist[row].count(False) == 1:
                    leftoverX = foundlist[row].index(False)
                    
                    for t3 in range(len(x_with_block[row+1])):
                        # 1つ上の行に着目する
                        # 該当行の余り+1つ上の行の最も左のものを取得するケースを考える
                        x3 = x_with_block[row + 1][t3]
                        test_xs_xs = "xs_" + str(leftoverX) + str(shapelist[row][leftoverX]) + "_" + str(x3) + str(shapelist[row + 1][x3])
                        # Update foundlist and key_order if the key is valid
                        if lib.artdict[test_xs_xs] != False and foundlist[row + 1][x3] == False:
                            foundlist[row][leftoverX], foundlist[row + 1][x3] = True, True
                            key_order[row].append(test_xs_xs)
                            # Move on to next row
                            key_order = bruteforce(x_with_block = x_with_block, key_order = key_order, foundlist=foundlist, row = row + 1)
                            # Try other combinations of the x-coords if this key does not work.
                            # Remove the key from key_order, then update foundlist.
                            # Otherwise the key_order is valid, in which case just return key_order
                            key_order, foundlist = remove_if_deadend_2(key_order = key_order, foundlist = foundlist, row = row, test_xs_xs = test_xs_xs, leftoverX = leftoverX, x3 = x3)

                # Keep testing two x-coords while more than two blocks is remaining
                else:
                    key_order = bruteforce(x_with_block = x_with_block, key_order = key_order, foundlist=foundlist, row = row)
                    # Try other combinations of the x-coords if this key does not work.
                    # Remove the key from key_order, then update foundlist.
                    # Otherwise the key_order is valid, in which case just return key_order  
                    key_order, foundlist = remove_if_deadend(key_order = key_order, foundlist = foundlist, row = row, test_xs = test_xs, x1 = x1, x2 = x2)

    return key_order

# Rearrange key_order to make it more likely to be successful.
# 探索したkey_orderを再構成する
# ブロックの置く順番に矛盾が生じることを防ぐために様々な工夫を試みる
# input
#   bruteforce()により探索したkey_order
# output
#   rearrangeしたkey_order
def rearrange(shapelist, key_order, n):
    key_order_copy = copy.deepcopy(key_order)
    for row in range(1, n): # 各行
        for xs in range(len(key_order[row])): # 該当行の各組合せ
            test = key_order[row][xs]
            if test.count("_") == 1:          # 同じ行の組み合わせの場合
                # それぞれのx座標を確認し
                # もし左端に置くようなものがあればなるべく置く順番を後回しにする(おそらく何かと干渉するのを防ぐ意図があるはず)
                x1,x2 = int(test[3]),int(test[5]) 
                if shapelist[row - 1][x1] == "0" or shapelist[row - 1][x2] == "0":
                    key_order_copy[row].remove(test)
                    key_order_copy[row].append(test)

    for row in range(1, n): # 各行
        for xs in range(len(key_order[row])): # 該当行の各組合せ
            test = key_order[row][xs]
            # 異なる行の組み合わせの場合
            # 順番を変える（該当行を置く場合の一番最後に実行されるようにする(はず)）
            if test[5] == "_":                
                key_order_copy[row].remove(test)
                key_order_copy[row].append(test)

    return key_order_copy

# found list (探索済みの場所を管理する配列) における探索対象数は偶数でなければならない
# (2つのペアづつ組み合わせを探す方式であるため)
# 偶数でない場合は強制終了
def check_blocknumber(foundlist):
    zero = 0
    for l in foundlist:
        zero += l.count(False)
    if zero % 2 == 1:
        print(zero)
        print("This art has an odd number of blocks")
        sys.exit()

# --- main
import art_lib as lib   # 同階層のart_libをimport(組み合わせテーブル取得のため)
import random
import time

# --- 入力
print("number of rows:") # 行数
n = int(input())
print("shapes in 10 digits:")
# Receive input as 1D array, reverse it in bottom-to-top order
# 入力はコードの上から下の順番に与えるが、探索は下から実施するため配列を逆順にする
shapelist = receive_shapelist(n = n)

print("----------------------------")
for pr in shapelist:
    print(pr)

# 2D array of whether each dot has been found.
# True if blank or if the procedure is found.
# found list (探索済みの場所を管理する配列) を初期化する
foundlist = foundlist_init(n = n, shapelist = shapelist)
for pr in foundlist:
    print(pr)

# The number of blocks used in art must be even 
# found list (探索済みの場所を管理する配列) における探索対象数は偶数でなければならないのでチェックする
check_blocknumber(foundlist = foundlist)

# 2D array of x-coordinates with a block in each row
# Randomize x order within each row to change the search order each time 
x_with_block = x_with_block_init(n = n, foundlist=foundlist)

# key_order is an array of keys from artdict that can compose the art
# Implement bruteforce search to find key_order. Take 2 x-coords from x-with-block then check if procedure in artdict has been found.
key_order = [[] for i in range(n)] 
key_order = bruteforce(x_with_block = x_with_block, key_order = key_order, foundlist=foundlist, row = 0)
# Rearrange key_order to make it more likely to be successful.
# ブロックの置く順番に矛盾が生じることを防ぐために様々な工夫を試みる
key_order = rearrange(shapelist = shapelist, key_order = key_order, n = n)


path = '..\\tetris\\game_manager\\log_art.txt'

# 探索結果の出力
for pr in key_order:
    print("'" +"', '".join(map(str,pr))+"',")
    with open (path, mode ="a") as f:
        f.write("'" +"', '".join(map(str,pr))+"'" +"\n")

# lib.artdictの更新用
for row in key_order: # 各行
    for xs in row:    # 各行の組合せ
        output = lib.artdict[xs]
        print(", ".join(map(str,output))+ ",")
        with open (path, mode ="a") as f:
            f.write(", ".join(map(str,output))+ "," +"\n")

with open (path, mode ="a") as f:
    f.write("======================================================" +"\n")
