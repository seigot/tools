#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import subprocess
from argparse import ArgumentParser

def get_option(game_level, game_time, manual, use_sample, random_seed, resultlogfile, user_name, drop_speed, obstacle_height, obstacle_probability):
    argparser = ArgumentParser()
    argparser.add_argument('-l', '--game_level', type=int,
                           default=game_level,
                           help='Specify game level')
    argparser.add_argument('-t', '--game_time', type=int,
                           default=game_time,
                           help='Specify game time(s)')
    argparser.add_argument('-m', '--manual',
                           default=manual,
                           help='Specify if manual control')
    argparser.add_argument('-s', '--use_sample',
                           default=use_sample,
                           help='Specify if use sample')
    argparser.add_argument('-r', '--random_seed', type=int,
                           default=random_seed,
                           help='Specify random seed') 
    argparser.add_argument('-f', '--resultlogfile', type=str,
                           default=resultlogfile,
                           help='Specigy result log file path')
    argparser.add_argument('-u', '--user_name', type=str,
                           default=user_name,
                           help='Specigy user name')
    argparser.add_argument('--drop_speed', type=int,
                           default=drop_speed,
                           help='Specify drop_speed(s)')
    argparser.add_argument('--obstacle_height', type=int,
                           default=obstacle_height,
                           help='Specify obstacle height')
    argparser.add_argument('--obstacle_probability', type=int,
                           default=obstacle_probability,
                           help='Specify obstacle probability')
    return argparser.parse_args()

def testfunc(a):
    game_level = 1
    game_time = 1
    manual = 1
    use_sample = 1
    drop_speed = 1
    random_seed = 1
    user_name = "test"
    obstacle_height = 1
    obstacle_probability = 1
    resultlogfile = "test.json"
    args = get_option(game_level,
                      game_time,
                      manual,
                      use_sample,
                      random_seed,
                      resultlogfile,
                      user_name,
                      drop_speed,
                      obstacle_height,
                      obstacle_probability)

    print(args)

    if args.game_time >= 0:
        game_time = args.game_time

a=100
testfunc(a)

#sys.exit(1)

GAME_TIME=5

cmd = 'python game_manager/game_manager.py --game_time ' + str(GAME_TIME)
cp = subprocess.run(cmd, shell=True)
if cp.returncode != 0:
    print('ls failed.', file=sys.stderr)
    sys.exit(1)
