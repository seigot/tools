
import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

_id = int(input())  # id of your player.
board_size = int(input())

print("Debug messages...", _id, file=sys.stderr, flush=True)
print("Debug messages...", board_size, file=sys.stderr, flush=True)

# game loop
while True:
    for i in range(board_size):
        line = input()  # rows from top to bottom (viewer perspective).
        print("Debug messages...", line, file=sys.stderr, flush=True)

    action_count = int(input())  # number of legal actions for this turn.
    print("Debug messages...", action_count, file=sys.stderr, flush=True)
    for i in range(action_count):
        action = input()  # the action
        print("Debug messages...", action, file=sys.stderr, flush=True)


    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # a-h1-8
    # print("f3")
    print(action)
