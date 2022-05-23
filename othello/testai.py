import sys
import math
import random

def debug_print(*args, end="\n"): print("[debug]", *args, end=end, file=sys.stderr)

########## input ##########
# player_color            #
# board                   #
#                         #
# ex.)                    #
# 0                       #
#  ABCDEFGH               #
# 1........               #
# 2........               #
# 3........               #
# 4...01...               #
# 5...10...               #
# 6........               #
# 7........               #
# 8........               #
#                         #
########## output #########
# evaluation value        #
# stone location          #
#                         #
# ex.)                    #
# 0 f5                    #
###########################

board_size = 8

def coord_to_y(_coord):
    return (_coord + 1)

def coord_to_x(_coord):
    if _coord == 0:
        coord = 'a'
    elif _coord == 1:
        coord = 'b'
    elif _coord == 2:
        coord = 'c'
    elif _coord == 3:
        coord = 'd'
    elif _coord == 4:
        coord = 'e'
    elif _coord == 5:
        coord = 'f'
    elif _coord == 6:
        coord = 'g'
    elif _coord == 7:
        coord = 'h'
    return coord

def is_inside(y, x):
    if (0 <= y < board_size and 0 <= x < board_size):
        return True
    return False

def get_legal_grid_list(myColor, board):
    # init parameter
    hw=8
    board_is_legal = [[0 for j in range(hw)]for i in range(hw)] # hw*hw matrix
    dy = [0, 1, 0, -1, 1, 1, -1, -1] # for search all(8) direction
    dx = [1, 0, -1, 0, 1, -1, 1, -1] # for search all(8) direction

    # search all grid
    for y in range(hw):
        for x in range(hw):
            if board[y][x] != '.':
                # skip when already flipped
                continue
            legal_flag = False
            for dr in range(8):
                # search all direction
                is_opponent_stone = False
                is_my_stone = False
                ny = y
                nx = x
                # check target 1 direction
                for _ in range(hw - 1):
                    # update current target grid
                    ny += dy[dr]
                    nx += dx[dr]
                    if is_inside(ny, nx) == False or board[ny][nx] == '.':
                        # if outside, end search
                        # if vacant, end search
                        is_opponent_stone = False
                        break
                    elif int(board[ny][nx]) != myColor:
                        # if other player stone, continue search
                        is_opponent_stone = True
                    elif int(board[ny][nx]) == myColor:
                        # if my stone end search
                        is_my_stone = True
                        break
                if is_opponent_stone and is_my_stone:
                    legal_flag = True
                    break
            if legal_flag == True:
                board_is_legal[y][x] = 1 # legal
    debug_print("--")
    debug_print(board_is_legal)
    # return
    ll = []
    for y in range(hw):
        for x in range(hw):
            if board_is_legal[y][x] == 1:
                string = str(coord_to_x(x)) + str(coord_to_y(y))
                ll.append(string)
    debug_print(ll)
    return ll

# main loop
while True:
    # input --->
    myColor = int(input())
    debug_print(myColor)
    board = []
    for i in range(board_size):
        line = input()
        board.append(line)
        debug_print(line)
    # input <---
    ll = get_legal_grid_list(myColor, board)
    debug_print("---ll")
    debug_print(ll)
    ans = random.choice(ll)
    ans="0 "+ans
    debug_print(ans)

    print(ans)

