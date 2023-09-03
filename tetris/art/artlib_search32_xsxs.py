import sys
import subprocess
import copy
import numpy
import time


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

range_y = len(board)-1

refpoint_relative = [[0],
                    [[[0,-1],[0,1],[0,2]],[[-2,0],[-1,0],[1,0]]],
                    [[[0,-1],[0,1],[1,1]],[[-1,0],[1,0],[-1,1]],[[-1,-1],[0,-1],[0,1]],[[1,-1],[-1,0],[1,0]]],
                    [[[0,-1],[0,1],[-1,1]],[[-1,-1],[-1,0],[1,0]],[[0,-1],[1,-1],[0,1]],[[-1,0],[1,0],[1,1]]],
                    [[[0,-1],[1,0],[0,1]],[[0,1],[-1,0],[1,0]],[[0,-1],[-1,0],[0,1]],[[0,-1],[-1,0],[1,0]]],
                    [[[0,-1],[1,-1],[1,0]]],
                    [[[0,-1],[1,-1],[-1,0]],[[0,-1],[1,0],[1,1]]],
                    [[[-1,-1],[0,-1],[1,0]],[[1,-1],[1,0],[0,1]]]
                    ]

Xrange = [[0],
        [[0,10],[2,9]],
        [[0,9],[1,9],[1,10],[1,9]],
        [[1,10],[1,9],[0,9],[1,9]],
        [[0,9],[1,9],[1,10],[1,9]],
        [[0,9]],
        [[1,9],[0,9]],
        [[1,9],[0,9]]
            ]

status = [[[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1],[0,0,0,1]],
board,  board,  board,  board,  board,  board, board,  board,  board ]

blockorder = [6,7,4,2,3,1,5]


def dfs(currentboard, num_move, status):
    global foundflag
    num_move += 1
    if num_move > maxmoves:
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
                            pass
                        else:
                            refpoint = [refpoint[0],refpoint[1]-1]

                            # simulate the board after the block is dropped
                            newboard[refpoint[1]][refpoint[0]] = shape
                            for add_grid in range(3):
                                newboard[refpoint[1] + refpoint_relative[shape][rotate][add_grid][1]][refpoint[0] +  refpoint_relative[shape][rotate][add_grid][0]] = shape

                            # clear fulllines
                            clearedboard = clearFullLines(currentboard = newboard)

                            contflag1 = CheckBottomRow(currentboard = clearedboard)
                            contflag2 = CheckTopRow(currentboard = clearedboard)
                            contflag3 = CheckHoles(currentboard = clearedboard)

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
                                    return ans
                                status[0][num_move-1] = [0,0,0,1]
                                    
                            else:
                                break
                            break

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

def CheckTopRow(currentboard):
    for num in range(3):
        TopRow = currentboard[num]
        for eachgrid in TopRow:
            if eachgrid != 0:
                return False
    return True

def clearFullLines(currentboard):
    board = currentboard
    for i in range(range_y):
        row = board[i]
        if row.count(0) == 0:
            for j in range(i,0,-1):
                board[j] = board[j-1]
            board[0] = [0,0,0,0,0,0,0,0,0,0]
            
    return board

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

def CheckClearRows(currentboard):
    for num in range(range_y - 1):
        TopRow = currentboard[num]
        for eachgrid in TopRow:
            if eachgrid != 0:
                return False
    return True


def search_artlib():
    global foundflag
    foundflag = False
    num_move = 0
    default_status = copy.deepcopy(status)
    ans = dfs(currentboard = status[1], num_move = num_move, status = default_status)
    if ans == None:
        return False
    return ans

def write_in_txt(ans):
    path = '..\\tetris\\game_manager\\log_art.txt'
    with open (path, mode ="a") as f:
        f.write('"xs_' + str(x1)+str(shape1)+str(x2)+str(shape2)+ '":' + str(ans)+ "," + "\n")

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
