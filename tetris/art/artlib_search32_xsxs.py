import sys
import subprocess
import copy
import numpy
import time

# 現在の盤面を表す2次元配列
board = [
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [9,9,9,9,9,9,9,9,9,9],
        ]
# boardの高さ方向のrange(1番下の9999999999はoffsetなので高さ方向にカウントしない)
range_y = len(board)-1
# 各shapeの回転の基準点以外のブロックの相対座標(shape1~7まで存在する)
refpoint_relative = [[0],
                    [[[0,-1],[0,1],[0,2]],[[-2,0],[-1,0],[1,0]]],
                    [[[0,-1],[0,1],[1,1]],[[-1,0],[1,0],[-1,1]],[[-1,-1],[0,-1],[0,1]],[[1,-1],[-1,0],[1,0]]],
                    [[[0,-1],[0,1],[-1,1]],[[-1,-1],[-1,0],[1,0]],[[0,-1],[1,-1],[0,1]],[[-1,0],[1,0],[1,1]]],
                    [[[0,-1],[1,0],[0,1]],[[0,1],[-1,0],[1,0]],[[0,-1],[-1,0],[0,1]],[[0,-1],[-1,0],[1,0]]],
                    [[[0,-1],[1,-1],[1,0]]],
                    [[[0,-1],[1,-1],[-1,0]],[[0,-1],[1,0],[1,1]]],
                    [[[-1,-1],[0,-1],[1,0]],[[1,-1],[1,0],[0,1]]]
                    ]
# 各shapeのx軸方向の探索範囲(1~7)
Xrange = [[0],
        [[0,10],[2,9]],
        [[0,9],[1,9],[1,10],[1,9]],
        [[1,10],[1,9],[0,9],[1,9]],
        [[0,9],[1,9],[1,10],[1,9]],
        [[0,9]],
        [[1,9],[0,9]],
        [[1,9],[0,9]]
            ]
# ブロックの組み合わせとboardの探索盤面, 最大8こ分
status = [[[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1]],
board,  board,  board,  board,  board,  board, board,  board,  board ]

# ブロックの組み合わせの並び
# 見つかりやすい順番に並べている (6,7は最も組み合わせを見つけやすい、1,5は最も組み合わせを見つけにくい)
blockorder = [6,7,4,2,3,1,5]

# xs_xsの組み合わせをDFS(深さ優先探索)により探索する
# input
#   currentboard:
#   num_move:
#   status:
# output
#   ans: 組み合わせのブロック
def dfs(currentboard, num_move, status):
    global foundflag
    num_move += 1
    if num_move > maxmoves:
        # 期待通りの盤面かどうかチェック
        # final check of the board
        # two x-coords must have the two shape indexes respectively. Others must be empty         
        printflag1 = CheckTwoBlocks(currentboard = status[maxmoves])
        # all rows apart from the bottom must be empty
        printflag2 = CheckClearRows(currentboard = status[maxmoves])

        if printflag1 == True and printflag2 == True:
            print("found one")
            foundflag = True
            # return the procedure that allows the two blocks to remain.
            return status[0]
    else:
        # search all combinations of shape, rotate and x-coord to see if it fits
        for shape in blockorder:
            for rotate in range(len(refpoint_relative[shape])):
                for Xgrid in range(Xrange[shape][rotate][0],Xrange[shape][rotate][1]):
                    # search for appropriate y-coord of refpoint that settles the block
                    # search from the top row and look for the first y-coord such that the grid to be placed is already filled.
                    # the appropriate y-coord of the refpoint is the one above it
                    for Ygrid in range(2,range_y+1):
                        newboard = copy.deepcopy(currentboard)
                        refpoint = [Xgrid,Ygrid]
                        
                        gridref = newboard[refpoint[1]][refpoint[0]] 
                        grid0 = newboard[refpoint[1] + refpoint_relative[shape][rotate][0][1]][refpoint[0] +  refpoint_relative[shape][rotate][0][0]]
                        grid1 = newboard[refpoint[1] + refpoint_relative[shape][rotate][1][1]][refpoint[0] +  refpoint_relative[shape][rotate][1][0]]
                        grid2 = newboard[refpoint[1] + refpoint_relative[shape][rotate][2][1]][refpoint[0] +  refpoint_relative[shape][rotate][2][0]]
                        if gridref == 0 and grid0 == 0 and grid1 == 0 and grid2 == 0:
                            # 1つでも0でない(既存の盤面と重なりが生じる)部分を見つけたいと思っており、
                            # それに該当しない場合はスキップ
                            pass
                        else:
                            # 1つでも0でない部分を見つけたら、その1つ上に対象のミノを置けるようにする
                            # 具体的にはここでrefpointを更新する(Ygrid=Ygrid-1に更新する)
                            refpoint = [refpoint[0],refpoint[1]-1]

                            # simulate the board after the block is dropped
                            newboard[refpoint[1]][refpoint[0]] = shape
                            for add_grid in range(3):
                                newboard[refpoint[1] + refpoint_relative[shape][rotate][add_grid][1]][refpoint[0] +  refpoint_relative[shape][rotate][add_grid][0]] = shape

                            # clear fulllines
                            clearedboard = clearFullLines(currentboard = newboard)
                            # 各種チェック(後述)
                            contflag1 = CheckBottomRow(currentboard = clearedboard)
                            contflag2 = CheckTopRow(currentboard = clearedboard)
                            contflag3 = CheckHoles(currentboard = clearedboard)
                            # チェックが全てOKであれば探索対象として妥当な盤面なので次の探索に移る
                            if contflag1 == True and contflag2== True and contflag3 == True:
                                status[0][num_move-1][0] = shape
                                status[0][num_move-1][1] = rotate
                                status[0][num_move-1][2] = Xgrid
                                status[num_move] = clearedboard
                                path = '..\\tetris\\game_manager\\log_art.txt'
                                with open (path, mode ="a") as f:
                                    f.write(str(status[0]) + "\n")

                                ans = dfs(currentboard = status[num_move],num_move = num_move,status = status)
                                if foundflag == True:
                                    # 見つかったらansを返す
                                    return ans
                                # 見つからなかったらstatusを元に戻す
                                status[0][num_move-1] = [0,0,0,1]
                                    
                            else:
                                break
                            break

# 一番下の行を確認し
# 探索対象のブロック(x1,shape1),(x2,shape2)以外のブロックがないことをチェックする
# 探索対象ではないブロックが1つでも存在していたらFalse
def CheckBottomRow(currentboard):
    BottomRow = currentboard[range_y - 1]
    i = 0
    for eachgrid in BottomRow:
        if eachgrid != 0:
            if (i == x1 and eachgrid == shape1) or (i == x2 and eachgrid == shape2):
                pass
            else:
                return False
        i += 1
    return True


# 一番下の行を確認し、
# 探索結果が探索対象の組み合わせ(x1shape1_x2shape2)であるかどうかをチェックする
# 探索対象の組み合わせである: True
# そうでない: False
def CheckTwoBlocks(currentboard):
    board = currentboard
    Y = range_y -1 
    for X in range(10):
        TestShape = board[Y][X]
        # first x-coord and shape1
        if X == x1:
            if TestShape != shape1:
                return False
        # second x-coord and shape2
        elif X == x2:
            if TestShape != shape2:
                return False
        # others must be empty
        else:
            if TestShape != 0:
                return False
    return True

# 4*8=32の探索を前提としているのでそれでブロックを消せない場合は探索対象外とする
# 具体的にはboardの上3行にブロックが1つでも存在していたらFalseとする
def CheckTopRow(currentboard):
    for num in range(3):
        TopRow = currentboard[num]
        for eachgrid in TopRow:
            if eachgrid != 0:
                return False
    return True

# 1行揃ったら対象行を削除する
def clearFullLines(currentboard):
    board = currentboard
    for i in range(range_y):
        row = board[i]
        if row.count(0) == 0:
            for j in range(i,0,-1):
                # ここで削除対象行を基準にboardを一段ずらす
                board[j] = board[j-1]
            board[0] = [0,0,0,0,0,0,0,0,0,0]
            
    return board

# Holeが存在しているかどうかチェック
# boardの下から上の順に操作してHoleが存在していたらFalse
# Holeが存在していなければTrue
def CheckHoles(currentboard):
    board = currentboard
    for X in range(10):
        holecandidate = False
        for Y in range(range_y - 2,0,-1):
            if board[Y][X] == 0:
                holecandidate = True
            else:
                if holecandidate == True:
                    return False

    return True

# 一番下の行を除いて全て削除できているかを確認する
def CheckClearRows(currentboard):
    for num in range(range_y - 1):
        TopRow = currentboard[num]
        for eachgrid in TopRow:
            if eachgrid != 0:
                return False
    return True

# xs_xsの組み合わせを探索する
def search_artlib():
    global foundflag
    foundflag = False
    num_move = 0
    default_status = copy.deepcopy(status)
    ans = dfs(currentboard = status[1], num_move = num_move, status = default_status)
    if ans == None:
        return False
    return ans

# 該当の組み合わせの探索結果をログファイルに出力する
# ans
# True: 見つかった(見つかった場合は組み合わせをリスト形式で出力する)
# False: 見つからない
def write_in_txt(ans):
    path = '..\\tetris\\game_manager\\log_art.txt'
    with open (path, mode ="a") as f:
        f.write('"xs_' + str(x1)+str(shape1)+str(x2)+str(shape2)+ '":' + str(ans)+ "," + "\n")

# ミノ1つ4ブロック*8 = 32(3行+2つ)の範囲で組み合わせを探索する
maxmoves = 8
# for each combination of two x-coords and two shapes
for x1 in range(10):
    for x2 in range(x1+1,10-x1+1):
        for shape1 in blockorder:
            for shape2 in blockorder:
                print(x1,shape1,x2,shape2)
                #  return the procedure that allows the two blocks to remain. Return False if not found.
                ans = search_artlib()
                # write the ans in txt
                write = write_in_txt(ans = ans)

print("All done")
