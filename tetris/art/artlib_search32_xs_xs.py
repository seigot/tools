import sys
import subprocess
import copy
import numpy
import time

# Initial board for simulation with "9" being a sentinel
board_init = [
        [9,9,9,9,9,9,9,9,9,9,9,9],
        [9,0,0,0,0,0,0,0,0,0,0,9],
        [9,0,0,0,0,0,0,0,0,0,0,9],
        [9,0,0,0,0,0,0,0,0,0,0,9],
        [9,9,9,9,9,9,9,9,9,9,9,9],
        ]

range_y = len(board_init)-1

# Arrangement of blocks arond the ref point.
# [block index][rotation][three dots][0 = x-coord, 1 = y-coord]
refpoint_relative = [[0],
                    [[[0,-1],[0,1],[0,2]],[[-2,0],[-1,0],[1,0]]],
                    [[[0,-1],[0,1],[1,1]],[[-1,0],[1,0],[-1,1]],[[-1,-1],[0,-1],[0,1]],[[1,-1],[-1,0],[1,0]]],
                    [[[0,-1],[0,1],[-1,1]],[[-1,-1],[-1,0],[1,0]],[[0,-1],[1,-1],[0,1]],[[-1,0],[1,0],[1,1]]],
                    [[[0,-1],[1,0],[0,1]],[[0,1],[-1,0],[1,0]],[[0,-1],[-1,0],[0,1]],[[0,-1],[-1,0],[1,0]]],
                    [[[0,-1],[1,-1],[1,0]]],
                    [[[0,-1],[1,-1],[-1,0]],[[0,-1],[1,0],[1,1]]],
                    [[[-1,-1],[0,-1],[1,0]],[[1,-1],[1,0],[0,1]]]
                    ]

# Arrangement of blocks in an 1D array starting from top-left
# Useful in standardising into config format from test_board
dot_relative = [[0],
                [[-10, 0, 10, 20], [-2, -1, 0, 1]],
                 [[-10, 0, 10, 11], [-1, 0, 1, 9], [-11, -10, 0, 10], [-9, -1, 0, 1]],
                 [[-10, 0, 9, 10], [-11, -1, 0, 1], [-10, -9, 0, 10], [-1, 0, 1, 11]],
                 [[-10, 0, 1, 10], [-1, 0, 1, 10], [-10, -1, 0, 10], [-10, -1, 0, 1]], 
                 [[-10, -9, 0, 1]], 
                 [[-10, -9, -1, 0], [-10, 0, 1, 11]],
                 [[-11, -10, 0, 1], [-9, 0, 1, 10]]
                ]


adj_zero_init = [0 for i in range(30)]

blockorder = [6,7,4,2,3,1,5]

def search_filledboard(board):
    # Assume that all blocks in the bottom row is filled, except the one to be searched
    board[4][x1+1] = 0
    # Empty a cell in the top row
    board[0][x2+1] = 0
    # All rotations of the two shapes to fit the top and bottom rows
    testboards = fit_shapes(board = board)

    for testboard in testboards:
        notfoundflag = False
        # 1D array of the number of blank cells adjecent to each cell
        # "9" as dummy figure if the cell is already filled
        adj_zero = adj_zero_from_testboard(board = testboard)

        rnd = 1
        # 6個分探索する(2つ分は事前に探索済みのため)
        for block in range(6):
            adj = []
            rnd += 1
            # Place a dot at where most likely to be deadlock
            testboard, adj_zero, adj = fill_most_isolated(rnd = rnd, testboard = testboard, adj_zero = adj_zero, adj = adj)
            if adj == []:
                notfoundflag = True
                continue
            # Place three dots from adj 
            for j in range(3):
                testboard, adj_zero, adj = fill_isolated_from_adj(rnd = rnd, testboard = testboard, adj_zero = adj_zero, adj = adj)        
                if adj == [] and j != 2:
                    notfoundflag = True
                    break
        if notfoundflag == False:
            return testboard

    return False

# はみ出ていないかどうかチェック
# board_initに元々9(番兵)を与えていた部分が別の数値に変わっていたらはみ出ていたと判定する
# 下側をチェックする
def check_bottom(currentboard):
    check = False
    if currentboard[4][x1+1] == 1 and currentboard[4].count(1) == 1:
        check = True
    return check
# 上側をチェックする
def check_top(currentboard):
    check = False
    if currentboard[0][x2+1] == 8 and currentboard[0].count(8) == 1:
        check = True
    return check
# 左右の端をチェックする
def check_sides(currentboard):
    for i in range(len(currentboard)):
        if currentboard[i][0] != 9:
            return False
        if currentboard[i][len(currentboard[i])-1] != 9:
            return False
    return True
# ブロック全体を見渡して、1(下側),8(上側)が期待通りはまっているかチェックする
# 期待通りであれば4となる
def check_1and8(currentboard):
    one,eight = 0,0
    for y in range(len(currentboard)):
        for x in range(len(currentboard[y])):
            dot = currentboard[y][x]
            if dot == 1:
                one += 1
            if dot == 8:
                eight += 1
    if one == 4 and eight == 4:
        return True
    else:
        return False

def fit_shapes(board):
    # All rotations to fit the bottom row
    testboards = find_shape1(board = board)
    # All rotations to fit the top row
    testboards = find_shape2(boards = testboards)
    return testboards

# shape1が下側の行に全てハマる組みわせを全て見つけ出す
def find_shape1(board):
    applicable_board = []
    # The block to fill the bottom row would appear no further than two x-coords away from the ref point
    for x in range(x1,x1+3):
        # Try each rotation
        for rotate in refpoint_relative[shape1]:
            testboard = copy.deepcopy(board)
            # Place four dots around refpoint
            for dot in rotate:
                testboard[3][x] = 1  # 2 if shapeindex == 1
                # y-coord is no greater than len(y)-1, x-coord is no greater than len(x) -1
                testboard[min(len(testboard)-1,3 + dot[1])][min(len(board[0])-1, x + dot[0])] = 1
            # Check if valid
            contflag1 = check_sides(currentboard = testboard)
            contflag2 = check_bottom(currentboard = testboard)
            if contflag1 == True and contflag2 == True:
                applicable_board.append(testboard)
                
    return applicable_board

# shape1が上側の行に全てハマる組みわせを全て見つけ出す
def find_shape2(boards):
    applicable_board = []
    for testboard_ in boards:
        for x in range(x2,x2+3):
            for rotate in refpoint_relative[shape2]:
                testboard = copy.deepcopy(testboard_)
                for dot in rotate:
                    testboard[1][x] = 8 # 2 if shapeindex == 1
                    # x-coord is no greater than len(x) -1
                    testboard[1 + dot[1]][min(len(board[0])-1, x + dot[0])] = 8
                # Check if valid
                contflag1 = check_sides(currentboard = testboard)
                contflag2 = check_top(currentboard = testboard)
                contflag3 = check_1and8(currentboard = testboard)                
                if contflag1 == True and contflag2 == True and contflag3 == True:
                    applicable_board.append(testboard)

    return applicable_board
# 10*3のブロックに着目する
# board_init上、既にブロックを仮置きしている部分は9を与える
# NSWE分の大きさが入る座標は+1を与える（ここがよくわからない）
def adj_zero_from_testboard(board):
    adj_zero = copy.deepcopy(adj_zero_init)
    for dot_ in range(len(adj_zero)):
        xaxis = dot_ % 10 + 1
        yaxis = dot_ // 10 + 1
        if board[yaxis][xaxis] != 0:
            adj_zero[dot_] = 9
        else:
            NSWE = [(0,1),(0,-1),(1,0),(-1,0)]
            for nswe in NSWE:
                if board[yaxis + nswe[0]][xaxis + nswe[1]] == 0:
                    adj_zero[dot_] += 1
    return adj_zero

# 何をするのか..
def fill_most_isolated(rnd,testboard,adj_zero, adj):
    isolated = 0
    count = 0
    testdot_ = 4
    endflag = False
    for eachdot_ in adj_zero:
        if testdot_ >= eachdot_ :
            testdot_ = eachdot_
            isolated = count
        count += 1
    # Place a dot at where most stuck
    testboard = fill_testboard(rnd = rnd, testboard = testboard, isolated = isolated)
    # Update adj_zero, the number of blank cells adjecent to each cell
    # Update adj, indexes of cells adjecent to dots that have been placed in each round
    adj_zero,adj = fill_adj_and_adj_zero(isolated = isolated, adj_zero = adj_zero, adj = adj)

    return testboard, adj_zero, adj

# 何をするのか..
def fill_isolated_from_adj(rnd,testboard,adj_zero, adj):
    isolated = 0
    testdot_ = 4
    # Choose the most isolated cell from adj
    for eachdot_ in adj:
        if testdot_ >= adj_zero[eachdot_] :
            testdot_ = adj_zero[eachdot_]
            isolated = eachdot_
    # Remove the chosen from adj
    adj.remove(isolated)

    testboard = fill_testboard(rnd = rnd, testboard = testboard, isolated = isolated)
    # Update adj_zero, the number of blank cells adjecent to each cell
    # Update adj, indexes of cells adjecent to dots that have been placed in each round
    adj_zero,adj = fill_adj_and_adj_zero(isolated = isolated, adj_zero = adj_zero, adj = adj)

    return testboard, adj_zero, adj


def fill_testboard(rnd, testboard, isolated):
    xaxis = isolated % 10 + 1
    yaxis = isolated // 10 + 1
    testboard[yaxis][xaxis] = rnd
    return testboard

# 何をするのか..
def fill_adj_and_adj_zero(isolated, adj_zero, adj):
    # "9" as dummy figure if the cell is already filled
    adj_zero[isolated] = 9
    adj = set(adj)
    # If the cell on right is blank
    if isolated % 10 != 9 and adj_zero[isolated + 1] != 9:
        adj_zero[isolated + 1] -= 1
        adj.add(isolated + 1)
    # If the cell on left is blank
    if isolated % 10 != 0 and adj_zero[isolated - 1] != 9:
        adj_zero[isolated - 1] -= 1
        adj.add(isolated - 1)
    # If the cell below is blank
    if isolated // 10 != 2 and adj_zero[isolated + 10] != 9:
        adj_zero[isolated + 10] -= 1
        adj.add(isolated + 10)
    # If the cell above is blank
    if isolated // 10 != 0 and adj_zero[isolated - 10] != 9:
        adj_zero[isolated - 10] -= 1
        adj.add(isolated - 10)
    adj = list(adj)
    adj.sort()
    return adj_zero,adj

# 何をするのか..
def find_constraint(board):
    constraint = [set() for i in range(10)]
    for x in range(10):
        # Prior is a set of figures that have appeared in each column
        prior = set()
        for y in range(4): 
            prior.add(board[4-y][x+1])
            # For each figure get the figures that should be placed before it
            constraint[board[4-y][x+1]] = constraint[board[4-y][x+1]].union(prior)
    for s in range(len(constraint)):
        # Exclude from the constraint the figure itself as well as 9 as sentinel
        constraint[s].discard(s)
        constraint[s].discard(9)
    return constraint

# 何をするのか..
def find_shapeorder(board,constraint):
    used = [False for i in range(9)]
    # Better to place them from both sides to avoid unexpected game overs
    x_order = [1,10,2,9,3,8,4,7,5,6]
    shapeorder = []
    while used.count(False) > 0:
        for x in x_order:
            revisit = False
            for y in range(4):
                shape = board[4 - y][x]
                # A shape can only be placed if all blocks to be placed have been placed.
                if used[shape-1] == False and constraint[shape] == set():
                    shapeorder.append(shape)
                    used[shape-1] = True
                    # A figure is no longer a constraint if it have been placed
                    for s in range(len(constraint)):
                        constraint[s].discard(shape)
                    revisit = True

                if revisit == True:
                    continue
            if revisit == True:
                continue
    shapeorder.remove(9)
    return shapeorder

# 何をするのか..
def find_dotorder(board,shapeorder):
    dotorder = [[] for i in range(8)]
    for y in range(5):
        for x in range(len(board[y])):
            shape = board[y][x]
            if shape != 9:
                dotorder[shape-1].append((y*10 + x - 1))
    dotorder = [sorted(each) for each in dotorder ]
    ans = []
    for shape in shapeorder:
        ans.append(dotorder[shape-1])
    return ans

def convert_json_format(dot):
    flag = False
    while flag == False:
        dot4 = dot[0:4]
        ans = []
        # Subtract 1 from each index of the four dots until it matches with one of the dot_relative
        # Given that each refpoint in dot_relative is expressed as zero, the x-coord of the original refpoint is the difference from its original index 
        for shape in range(len(dot_relative)):
            for rotate in range(len(dot_relative[shape])):
                if dot_relative[shape][rotate] == dot4:
                    ans.append(shape)
                    ans.append(rotate)
                    ans.append((dot[4]-dot[0]) % 10)
                    ans.append(1)
                    return ans
        for i in range(4):
            dot[i] -= 1 
        if min(dot) <= -13:
            flag = True

def adjust_dotorder_for_smallest(dotorder):
    for i in range(len(dotorder)):
        smallest = min(dotorder[i])
        for j in range(4):
            dotorder[i][j] = dotorder[i][j] - smallest
        dotorder[i].append(smallest)
    return dotorder


def search_artlib(board):
    # Return a board that allows the two blocks to remain
    board = search_filledboard(board = board)
    if board != False:
        if board[0].count(0) > 0:
            time.sleep(15)
        """
        for pr in board:
            print(pr)
        """
        # Get appropriate block order
        # A block should be placed later than the blocks below it
        constraint = find_constraint(board = board)
        # Get order to place shapes based on the constraint 
        shapeorder = find_shapeorder(board = board, constraint = constraint)
        # Convert each shape into four dots expressed in an 1D array
        dotorder = find_dotorder(board = board, shapeorder = shapeorder)
        # Convert indexes of four dots into shape index, rotation and the x-coord of ref point
        # Subtract each index by its smallest to simplify later calculations
        # The fourth element of each list, previously the smallest index, is used to obtain x-coord of each refpoint
        dotorder = adjust_dotorder_for_smallest(dotorder = dotorder)

        output = []
        for dot in dotorder:
            # Compare dotorder and dot_relative and standardise to art-mode format
            ans = convert_json_format(dot)
            output.append(ans)
        return output

    else:
        return False


def merge_artlib():
    if key in artdict.keys():
        with open (path, mode ="a") as f:
            f.write('"'+ key + '":' + str(artdict[key]) + "\n")
    else:
        with open (path, mode ="a") as f:
            f.write('"'+ key + '":' + "False," + "\n")

def writeNone():
    with open (path, mode ="a") as f:
        f.write('"xs_' + str(x1)+str(shape1)+"_"+str(x2)+str(shape2)+ '":' + "False," + "\n")

#"""
import art_lib as lib
artdict = lib.artdict
maxblock = 8
block = 0
path = '..\\tetris\\game_manager\\log_art.txt'
# for each combination of two x-coords and shape indexes 
for x1 in range(10):
    for x2 in range(10):
        for shape1 in blockorder:
            for shape2 in blockorder:
                # Standardised key in artdict is xs_00_00
                key = "xs_" + str(x1)+str(shape1)+"_"+str(x2)+str(shape2)
                print(key)

                if artdict[key] == False:
                    board = copy.deepcopy(board_init)
                    # Return a procedure that allows the two blocks to remain. Return False if not found.
                    ans = search_artlib(board = board)
                    print(ans)
                    with open (path, mode ="a") as f:
                        f.write('"'+ key + '":' + str(ans) + ","+"\n")
                else:
                    with open (path, mode ="a") as f:
                        f.write('"'+ key + '":' + str(artdict[key]) + ","+"\n")

print("All done")
