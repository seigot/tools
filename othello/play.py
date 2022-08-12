# -*- coding: utf-8 -*-

import subprocess
from othello_py import *
import tkinter
import sys

offset_y = 10
offset_x = 10
rect_size = 60
circle_offset = 3

ai_player = int(input('AI moves (0: black 1: white): '))
ai2_player = 1 - ai_player
#ai_exe = subprocess.Popen('./a.exe'.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
ai_exe = subprocess.Popen('python testai.py'.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
ai2_exe = subprocess.Popen('python testai2.py'.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
#ai_exe.stdin.write((str(ai_player) + '\n').encode('utf-8'))
#ai_exe.stdin.flush()
record = ''
vals = []


o = None
legal_buttons = []

app = tkinter.Tk()
app.geometry('1000x700')
app.title('Egaroucid5')
canvas = tkinter.Canvas(app, width=1000, height = 700)
pixel_virtual = tkinter.PhotoImage(width=1, height=1)

def on_closing():
    global ai_exe
    global ai2_exe
    print("on_closing")
#    app.quit()
#    app.destroy()
    ai_exe.kill()
    ai2_exe.kill()
    app.destroy()
    sys.exit(0)

app.protocol("WM_DELETE_WINDOW", on_closing)

for y in range(hw):
    for x in range(hw):
        canvas.create_rectangle(offset_x + rect_size * x, offset_y + rect_size * y, offset_x + rect_size * (x + 1), offset_y + rect_size * (y + 1), outline='black', width=2, fill='#16a085')

stone_str = tkinter.StringVar()
stone_str.set('*Black 2 - 2 White ')
stone_label = tkinter.Label(canvas, textvariable=stone_str, font=('', 30))
stone_label.place(x=250, y=600, anchor=tkinter.CENTER)

val_str = tkinter.StringVar()
val_str.set('value: 0')
val_label = tkinter.Label(canvas, textvariable=val_str, font=('', 20))
val_label.place(x=10, y=650)

def start():
    global o, record, vals, ai_player
    record = ''
    vals = [-1000 for _ in range(60)]
    o = othello()
    o.check_legal()
    show_grid()

start_button = tkinter.Button(canvas, text='Start', command=start)
start_button.place(x=600, y=10)

def end_game():
    result = o.n_stones[1 - ai_player] - o.n_stones[ai_player]
    if result > 0:
        result += hw2 - sum(o.n_stones)
    elif result < 0:
        result -= hw2 - sum(o.n_stones)
    on_closing()

def translate_coord(y, x):
    return chr(ord('a') + x) + str(y + 1)

def ai():
    global clicked, record
    print("---")
    print(str(ai_player))
    ai_exe.stdin.write((str(ai_player) + '\n').encode('utf-8'))
    ai_exe.stdin.flush()
    grid_str = ''
    for i in range(hw):
        for j in range(hw):
            grid_str += '0' if o.grid[i][j] == 0 else '1' if o.grid[i][j] == 1 else '.'
        grid_str += '\n'
    print(grid_str)
    ai_exe.stdin.write(grid_str.encode('utf-8'))
    ai_exe.stdin.flush()
    val, coord = ai_exe.stdout.readline().decode().split()
    print("---")
    print("out!!", val, coord)
    val = float(val)
    y = int(coord[1]) - 1
    x = ord(coord[0]) - ord('a')
    vals[sum(o.n_stones) - 4] = val
    val_str.set('value: ' + str(val))
    record += translate_coord(y, x)
    print(y, x)
    clicked = True
    o.move(y, x)
    if not o.check_legal():
        o.player = 1 - o.player
        if not o.check_legal():
            o.print_info()
            o.player = -1
            print('end')
            end_game()
    s = ''
    if o.player == 0:
        s += '*'
    else:
        s += ' '
    s += 'Black '
    s += str(o.n_stones[0])
    s += ' - '
    s += str(o.n_stones[1])
    s += ' White'
    if o.player == 1:
        s += '*'
    else:
        s += ' '
    stone_str.set(s)
    #o.print_info()
    show_grid()

def ai2():
    global clicked, record
    print("---")
    print(str(ai2_player))
    ai2_exe.stdin.write((str(ai2_player) + '\n').encode('utf-8'))
    ai2_exe.stdin.flush()
    grid_str = ''
    for i in range(hw):
        for j in range(hw):
            grid_str += '0' if o.grid[i][j] == 0 else '1' if o.grid[i][j] == 1 else '.'
        grid_str += '\n'
    print(grid_str)
    ai2_exe.stdin.write(grid_str.encode('utf-8'))
    ai2_exe.stdin.flush()
    val, coord = ai2_exe.stdout.readline().decode().split()
    print("---")
    print("out!!", val, coord)
#    exit(0)
    val = float(val)
    y = int(coord[1]) - 1
    x = ord(coord[0]) - ord('a')
    vals[sum(o.n_stones) - 4] = val
    val_str.set('value: ' + str(val))
    record += translate_coord(y, x)
    print(y, x)
    clicked = True
    o.move(y, x)
    if not o.check_legal():
        o.player = 1 - o.player
        if not o.check_legal():
            o.print_info()
            o.player = -1
            print('end')
            end_game()
    s = ''
    if o.player == 0:
        s += '*'
    else:
        s += ' '
    s += 'Black '
    s += str(o.n_stones[0])
    s += ' - '
    s += str(o.n_stones[1])
    s += ' White'
    if o.player == 1:
        s += '*'
    else:
        s += ' '
    stone_str.set(s)
    #o.print_info()
    show_grid()

def get_coord(event):
    global clicked, record
    # tkinterへの入力を取得
    y = int(event.widget.cget('text')[0])
    x = int(event.widget.cget('text')[2])
    record += translate_coord(y, x)
    print(y, x)
    clicked = True
    # 入力
    o.move(y, x)
    if not o.check_legal():
        o.player = 1 - o.player
        if not o.check_legal():
            o.print_info()
            o.player = -1
            print('end')
            end_game()
    s = ''
    if o.player == 0:
        s += '*'
    else:
        s += ' '
    s += 'Black '
    s += str(o.n_stones[0])
    s += ' - '
    s += str(o.n_stones[1])
    s += ' White'
    if o.player == 1:
        s += '*'
    else:
        s += ' '
    stone_str.set(s)
    #o.print_info()
    show_grid()

def show_grid():
    global clicked, legal_buttons
    for button in legal_buttons:
        button.place_forget()
    legal_buttons = []

    # 描画する
    # ユーザからの入力を待つ??
    for y in range(hw):
        for x in range(hw):
            try:
                canvas.delete(str(y) + '_' + str(x))
            except:
                pass
            if o.grid[y][x] == vacant:
                continue
            color = ''
            if o.grid[y][x] == black:
                color = 'black'
            elif o.grid[y][x] == white:
                color = 'white'
            elif o.grid[y][x] == legal:
                if o.player != ai_player:
                    # ユーザ入力用のボタンを埋め込む
                    color = '#3498db'
                    legal_buttons.append(tkinter.Button(canvas, image=pixel_virtual, width=rect_size - circle_offset * 2, height=rect_size - circle_offset * 2, bg=color, text=str(y) + '_' + str(x)))
                    legal_buttons[-1].bind('<ButtonPress>', get_coord)
                    legal_buttons[-1].place(y=offset_y + rect_size * y, x=offset_x + rect_size * x)
                continue
            canvas.create_oval(offset_x + rect_size * x + circle_offset, offset_y + rect_size * y + circle_offset, offset_x + rect_size * (x + 1) - circle_offset, offset_y + rect_size * (y + 1) - circle_offset, width=0, fill=color, tag=str(y) + '_' + str(x))
    if o.player == ai_player:
        app.after(300, ai)
    else: #add
        app.after(300, ai2) #add


canvas.place(y=0, x=0)
#start()
app.after(10, start) #add
print("mainloop")
app.mainloop()
