#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import pprint
import copy

import torch
import torch.nn as nn
from deep_q_network import DeepQNetwork
from collections import deque
from tensorboardX import SummaryWriter

import os
import shutil
from random import random, randint, sample
import numpy as np

class Block_Controller(object):

    # init parameter
    board_backboard = 0
    board_data_width = 0
    board_data_height = 0
    ShapeNone_index = 0
    CurrentShape_class = 0
    NextShape_class = 0

    def __init__(self):
        
        self.mode = None

    # GetNextMove is main function.
    # input
    #    nextMove : nextMove structure which is empty.
    #    GameStatus : block/field/judge/debug information. 
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : nextMove structure which includes next shape position and the other.
    def GetNextMove(self, nextMove, GameStatus):

        t1 = datetime.now()

        # print GameStatus
        print("=================================================>")
        pprint.pprint(GameStatus, width = 61, compact = True)

        # get data from GameStatus
        # current shape info
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        self.CurrentShape_class = GameStatus["block_info"]["currentShape"]["class"]
        # next shape info
        NextShapeDirectionRange = GameStatus["block_info"]["nextShape"]["direction_range"]
        self.NextShape_class = GameStatus["block_info"]["nextShape"]["class"]
        # current board info
        self.board_backboard = GameStatus["field_info"]["backboard"]
        # default board definition
        self.board_data_width = GameStatus["field_info"]["width"]
        self.board_data_height = GameStatus["field_info"]["height"]
        self.ShapeNone_index = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]
        self.mode = GameStatus["judge_info"]["mode"]
        strategy = (0, 0, 0, 0)

        if self.mode == "train_sample":

            #self.width = 10 #args.width
            #self.heigth = 20 #args.height
            #self.block_size = 30 #args.block_size
            #self.batch_size = 512 #args.batch_size
            #self.lr = 1e-3 #args.lr
            #self.gamma = 0.99 #args.gamma
            #self.initial_epsilon = 1 #args.initial_epsilon
            #self.final_epsilon = 1e-3 #args.final_epsilon
            #self.num_decay_epochs = 1500 #args.num_decay_epochs
            #self.num_epochs = 3000 #args.num_epochs
            #self.save_interval = 1000 #args.save_interval
            #self.replay_memory_size = 30000 #args.replay_memory_size
            self.log_path = "./tensorboard" #args.log_path
            self.saved_path = "./trained_models" #args.saved_path

            #self.model = torch.load("{}/tetris".format(self.saved_path), map_location=lambda storage, loc: storage)
            #self.model.eval()

            self.episode = 0
            self.step = 0
            self.num_states = 4
            self.num_actions = 1
            self.model = DeepQNetwork()
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
            self.criterion = nn.MSELoss()
            self.replay_memory = deque(maxlen=self.replay_memory_size)

            self.init_state_flag = True

            #self.state = None
            #self.next_state = None
            #self.action = None
            #self.reward = None

            #if os.path.isdir(self.log_path):
            #    shutil.rmtree(self.log_path)
            os.makedirs(self.log_path)

            #if os.path.isdir(self.saved_path):
            #    shutil.rmtree(self.saved_path)
            os.makedirs(self.saved_path)

            self.writer = SummaryWriter(self.log_path)

            # train -->
            backboard = GameStatus["field_info"]["backboard"]
            done = False

            print("### step ###")
            print(self.step)
            print("### episode ###")
            print(self.episode)

            if(self.init_state_flag == True):
                # init state
                fullLines_num, nHoles_num, nIsolatedBlocks_num, absDy_num = BLOCK_CONTROLLER_NEXT_STEP.calcEvaluationValueSample(backboard)
                self.state = np.array([fullLines_num, nHoles_num, nIsolatedBlocks_num, absDy_num])
                self.state = torch.from_numpy(self.state).type(torch.FloatTensor)

                self.init_state_flag = False

            next_actions, next_states = self.getStrategyAndStatelist(GameStatus)
            next_actions = np.array(next_actions)
            next_actions = torch.from_numpy(next_actions).type(torch.FloatTensor)
            next_states = np.array(next_states)
            next_states = torch.from_numpy(next_states).type(torch.FloatTensor)

            print("### next_actions ###")
            print(next_actions)

            print("### next_states ###")
            print(next_states)

            self.model.eval()
            with torch.no_grad():
                predictions = self.model(next_states)[:, 0]
                print("### predictions ###")
                print(predictions)
                
            epsilon = self.final_epsilon + (max(self.num_decay_epochs - self.episode, 0) * (self.initial_epsilon - self.final_epsilon) / self.num_decay_epochs)
            print("### epsilon ###")
            print(epsilon)
            u = random()
            random_action = u <= epsilon

            self.model.train()
            if random_action:
                print("### len(next states) ###")
                print(len(next_states))
                index = randint(0, len(next_states) - 1)
            else:
                index = torch.argmax(predictions).item()

            self.next_state = next_states[index, :]
            print("### self.next_state ###")
            print(self.next_state)
            self.action = next_actions[index]
            print("### self.action ###")
            print(self.action) # (rotation, position)

            nextMove["strategy"]["direction"] = self.action[0].item()
            nextMove["strategy"]["x"] = self.action[1].item()
            nextMove["strategy"]["y_operation"] = 1
            nextMove["strategy"]["y_moveblocknum"] = 0

            ####
            ####

            strategy = None
            LatestEvalValue = -100000
            # search with current block Shape
            for direction0 in CurrentShapeDirectionRange:
                # search with x range
                x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
                for x0 in range(x0Min, x0Max):
                    # get board data, as if dropdown block
                    board = self.getBoard(self.board_backboard, self.CurrentShape_class, direction0, x0)

                    # evaluate board
                    EvalValue = self.calcEvaluationValueSample(board)
                    # update best move
                    if EvalValue > LatestEvalValue:
                        strategy = (direction0, x0, 1, 1)
                        LatestEvalValue = EvalValue


                        if reset.
                        self.episode += 1
                        self.step = 0

        else:
            # if self.mode == "predict_sample":

            # predict -->
            self.saved_path = "./trained_models"
            self.model = torch.load("{}/tetris".format(self.saved_path), map_location=lambda storage, loc: storage)
            self.model.eval()

            # search best nextMove -->
            next_actions, next_states = self.getStrategyAndStatelist(GameStatus)
            next_actions = np.array(next_actions)
            next_actions = torch.from_numpy(next_actions).type(torch.FloatTensor)
            next_states = np.array(next_states)
            next_states = torch.from_numpy(next_states).type(torch.FloatTensor)

            predictions = self.model(next_states)[:, 0]
            index = torch.argmax(predictions).item()
            action = next_actions[index]

            print("===", datetime.now() - t1)
            nextMove["strategy"]["direction"] = action[0].item()
            nextMove["strategy"]["x"] = action[1].item()
            nextMove["strategy"]["y_operation"] = 1
            nextMove["strategy"]["y_moveblocknum"] = 0
            # search best nextMove <--
            # predict <--

        print(nextMove)
        print("###### SAMPLE CODE (mode:{}) ######".format(self.mode))
        return nextMove

    def getStrategyAndStatelist(self, GameStatus):

        # get data from GameStatus
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        CurrentShape_class = GameStatus["block_info"]["currentShape"]["class"]
        board_backboard = GameStatus["field_info"]["backboard"]

        # search best nextMove -->
        strategy = None
        strategy_list = []
        state_list = []
        # search with current block Shape
        for direction0 in CurrentShapeDirectionRange:
            # search with x range
            x0Min, x0Max = self.getSearchXRange(CurrentShape_class, direction0)
            for x0 in range(x0Min, x0Max):
                # get board data, as if dropdown block
                board = self.getBoard(board_backboard, CurrentShape_class, direction0, x0)

                strategy = [direction0, x0]
                strategy_list.append(strategy)
                fullLines_num, nHoles_num, nIsolatedBlocks_num, absDy_num = self.calcEvaluationValueSample(board)
                state_list.append([fullLines_num, nHoles_num, nIsolatedBlocks_num, absDy_num])
        return strategy_list, state_list

    def getSearchXRange(self, Shape_class, direction):
        #
        # get x range from shape direction.
        #
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction) # get shape x offsets[minX,maxX] as relative value.
        xMin = -1 * minX
        xMax = self.board_data_width - maxX
        return xMin, xMax

    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        coordArray = Shape_class.getCoords(direction, x, y) # get array from shape direction, x, y.
        return coordArray

    def getBoard(self, board_backboard, Shape_class, direction, x):
        # 
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.
        board = copy.deepcopy(board_backboard)
        _board = self.dropDown(board, Shape_class, direction, x)
        return _board

    def dropDown(self, board, Shape_class, direction, x):
        # 
        # internal function of getBoard.
        # -- drop down the shape on the board.
        # 
        dy = self.board_data_height - 1
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < self.board_data_height and (_yy + _y < 0 or board[(_y + _yy) * self.board_data_width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board = self.dropDownWithDy(board, Shape_class, direction, x, dy)
        return _board

    def dropDownWithDy(self, board, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        _board = board
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        for _x, _y in coordArray:
            _board[(_y + dy) * self.board_data_width + _x] = Shape_class.shape
        return _board

    def calcEvaluationValueSample(self, board):
        #
        # sample function of evaluate board.
        #
        width = self.board_data_width
        height = self.board_data_height

        # evaluation paramters
        ## lines to be removed
        fullLines = 0
        ## number of holes or blocks in the line.
        nHoles, nIsolatedBlocks = 0, 0
        ## absolute differencial value of MaxY
        absDy = 0
        ## how blocks are accumlated
        BlockMaxY = [0] * width
        holeCandidates = [0] * width
        holeConfirm = [0] * width

        ### check board
        # each y line
        for y in range(height - 1, 0, -1):
            hasHole = False
            hasBlock = False
            # each x line
            for x in range(width):
                ## check if hole or block..
                if board[y * self.board_data_width + x] == self.ShapeNone_index:
                    # hole
                    hasHole = True
                    holeCandidates[x] += 1  # just candidates in each column..
                else:
                    # block
                    hasBlock = True
                    BlockMaxY[x] = height - y                # update blockMaxY
                    if holeCandidates[x] > 0:
                        holeConfirm[x] += holeCandidates[x]  # update number of holes in target column..
                        holeCandidates[x] = 0                # reset
                    if holeConfirm[x] > 0:
                        nIsolatedBlocks += 1                 # update number of isolated blocks

            if hasBlock == True and hasHole == False:
                # filled with block
                fullLines += 1
            elif hasBlock == True and hasHole == True:
                # do nothing
                pass
            elif hasBlock == False:
                # no block line (and ofcourse no hole)
                pass

        # nHoles
        for x in holeConfirm:
            nHoles += abs(x)

        ### absolute differencial value of MaxY
        BlockMaxDy = []
        for i in range(len(BlockMaxY) - 1):
            val = BlockMaxY[i] - BlockMaxY[i+1]
            BlockMaxDy += [val]
        for x in BlockMaxDy:
            absDy += abs(x)

        #### maxDy
        #maxDy = max(BlockMaxY) - min(BlockMaxY)
        #### maxHeight
        #maxHeight = max(BlockMaxY) - fullLines

        ## statistical data
        #### stdY
        #if len(BlockMaxY) <= 0:
        #    stdY = 0
        #else:
        #    stdY = math.sqrt(sum([y ** 2 for y in BlockMaxY]) / len(BlockMaxY) - (sum(BlockMaxY) / len(BlockMaxY)) ** 2)
        #### stdDY
        #if len(BlockMaxDy) <= 0:
        #    stdDY = 0
        #else:
        #    stdDY = math.sqrt(sum([y ** 2 for y in BlockMaxDy]) / len(BlockMaxDy) - (sum(BlockMaxDy) / len(BlockMaxDy)) ** 2)


        # calc Evaluation Value
        score = 0
        score = score + fullLines * 10.0           # try to delete line 
        score = score - nHoles * 1.0               # try not to make hole
        score = score - nIsolatedBlocks * 1.0      # try not to make isolated block
        score = score - absDy * 1.0                # try to put block smoothly
        #score = score - maxDy * 0.3                # maxDy
        #score = score - maxHeight * 5              # maxHeight
        #score = score - stdY * 1.0                 # statistical data
        #score = score - stdDY * 0.01               # statistical data

        # print(score, fullLines, nHoles, nIsolatedBlocks, maxHeight, stdY, stdDY, absDy, BlockMaxY)
        #return score
        return fullLines, nHoles, nIsolatedBlocks, absDy

BLOCK_CONTROLLER_TRAIN_SAMPLE = Block_Controller()
