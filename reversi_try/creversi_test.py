import creversi

board = creversi.Board()

def is_Turn(board):
    print()
    if board.turn == creversi.WHITE_TURN:
        print("---WHITE_TURN---")
    else:
        print("---BLACK_TURN---")

def print_boarddata(board):
    print("piece_sum: ", board.piece_sum())
    print("board.legal_moves: ", board.legal_moves)
    for move in board.legal_moves:
        print(move)
        print(creversi.move_to_str(move))
    print("board.piece_num():", board.piece_num())
    print("board.opponent_piece_num():", board.opponent_piece_num())
    print("board.diff_num():", board.diff_num())
    print("board.puttable_num(): ", board.puttable_num())
    print(board)

is_Turn(board)
print_boarddata(board)

print("board.move_from_str('d3')")
board.move_from_str('d3')

is_Turn(board)
for move in board.legal_moves:
    print(creversi.move_to_str(move))
print_boarddata(board)

import numpy as np

# 局面のビットボード形式
bitboard = np.empty(1, creversi.dtypeBitboard)
board.to_bitboard(bitboard)
board.set_bitboard(bitboard, board.turn)
print(bitboard)

hoge=np.empty((1, 2, 8, 8), dtype=np.float32)
print(hoge)
#planes = np.empty(1, np.empty((1, 2, 8, 8), dtype=np.float32))
#board.piece_planes(planes[0])
#print(planes)

# 機械学習向け訓練データ形式
data = np.empty(1, creversi.TrainingData)
board.to_bitboard(data['bitboard'])
data['turn'] = board.turn
data['move'] = list(board.legal_moves)[0]
data['reward'] = 1
data['done'] = False
print(data)


###
# OpenAI Gymのインターフェースをサポートする。
import gym
import creversi.gym_reversi

env = gym.make('Reversi-v0').unwrapped
env.reset()
env.board
print(env.board)
move=19#"d3"
next_board, reward, done, _ = env.step(move)
print(env.board)
