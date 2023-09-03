shape_rev = [None, 1,3,2,4,5,7,6]
rotate_rev = [None,[0,1],[0,3,2,1],[0,3,2,1],[2,1,0,3],[0],[0,1],[0,1]]
x_rev = [9,8,7,6,5,4,3,2,1,0]
blockorder = [6,7,4,2,3,1,5]

import art_lib as lib

def reversedict(x1,shape1,x2,shape2):
    xs_base = "xs_" +str(x1) +str(shape1)+str(x2)+str(shape2)
    recipe = lib.artdict[xs_base]
    if recipe == False:
        return False

    x1,shape1,x2,shape2 = int(x1),int(shape1),int(x2),int(shape2)
    if x1 > x2:
        xs_to_create = "xs_" +str(x_rev[x1]) +str(shape_rev[shape1])+str(x_rev[x2])+str(shape_rev[shape2])
    else:
        xs_to_create = "xs_" +str(x_rev[x2]) +str(shape_rev[shape2])+str(x_rev[x1])+str(shape_rev[shape1])

    newrecipe = []
    for eachinst in recipe:
        newinst = [0,0,0,1]
        newinst[0] = shape_rev[eachinst[0]]
        newinst[1] = rotate_rev[eachinst[0]][eachinst[1]]
        newinst[2] = x_rev[eachinst[2]]


        adjx = 0
        if eachinst[0] == 6 and eachinst[1] == 1:
            adjx = -1
        if eachinst[0] == 7 and eachinst[1] == 1:
            adjx = -1
        if eachinst[0] == 5:
            adjx = -1
        if eachinst[0] == 1 and eachinst[1] == 1:
            adjx = 1

        newinst[2] += adjx

        newrecipe.append(newinst)
    return newrecipe

#reversedict
for x1 in range(4,10):
    for x2 in range(x1+1,10):
        for shape1 in blockorder:
            for shape2 in blockorder:
                xs_to_create = "xs_" +str(x1) +str(shape1)+str(x2)+str(shape2)
                if x1 > x2:
                    xs_base = "xs_" +str(x_rev[x1]) +str(shape_rev[shape1])+str(x_rev[x2])+str(shape_rev[shape2])
                else:
                    xs_base = "xs_" +str(x_rev[x2]) +str(shape_rev[shape2])+str(x_rev[x1])+str(shape_rev[shape1])
                newrecipe = reversedict(xs_base[3],xs_base[4],xs_base[5],xs_base[6])
                path = '..\\tetris\\game_manager\\log_art.txt'
                with open (path, mode ="a") as f:
                    f.write(str(xs_to_create) + ":" +str(newrecipe)+ ","+ "\n")

