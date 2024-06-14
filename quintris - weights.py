# Simple quintris program! v0.2
# D. Crandall, Sept 2021

from AnimatedQuintris import *
from SimpleQuintris import *
#from kbinput import *
import time, sys
from copy import deepcopy
import numpy as np
import itertools
import json

class HumanPlayer:
    def get_moves(self, quintris):
        print("Type a sequence of moves using: \n  b for move left \n  m for move right \n  n for rotation\n  h for horizontal flip\nThen press enter. E.g.: bbbnn\n")
        moves = input()
        return moves

    def control_game(self, quintris):
        while 1:
            c = get_char_keyboard()
            commands =  { "b": quintris.left, "h": quintris.hflip, "n": quintris.rotate, "m": quintris.right, " ": quintris.down }
            commands[c]()

#####
# This is the part you'll want to modify!
# Replace our super simple algorithm with something better
#
def get_cost(game_quintris, combo):
    
    a,b,c,d,e = combo

    temp = deepcopy(game_quintris)
    temp.down()
    temp_board = temp.get_board()

    boardlist = [[i for i in r] for r in temp_board]
    tlist = list(zip(*boardlist))
    cols_with_endx = [''.join(list(t) + ['x']).strip() for t in tlist]

    column_heights = [
        max([QuintrisGame.BOARD_HEIGHT - r for r in range(QuintrisGame.BOARD_HEIGHT - 1, 0, -1)
             if temp_board[r][c] == 'x'] + [0, ]) for c in range(QuintrisGame.BOARD_WIDTH)]

    avg_height = sum(column_heights)/QuintrisGame.BOARD_WIDTH
    max_height = max(column_heights)
    
    max_height_factor = 1
    if max_height > 10:
        max_height_factor = 3
    
    
    holes = sum([t.count(' ') for t in cols_with_endx])

    # Code to check if lines cleared
    linescleared = sum([1 if r.count("x") == QuintrisGame.BOARD_WIDTH else 0 for r in boardlist])

    # no of pits
    pitscount = sum([1 if t.count(" ") == QuintrisGame.BOARD_HEIGHT else 0 for t in tlist])

    bumpiness = [len(t) - 1 for t in cols_with_endx]
    bumpinesscount = sum([np.abs(i - j) for i, j in zip(bumpiness, bumpiness[1:])])

    # Number of columns with atleast one hole
    col_with_holes = sum([1 if " " in i else 0 for i in cols_with_endx])

    # print([(max(column_heights)), holes, linescleared, pitscount, bumpinesscount, 5 * col_with_holes2])
    return a*holes + b*bumpinesscount + c*linescleared + d*pitscount + e*max_height

def move_right_left(game_qunitris, successor, s, combo):
    piece_length = len(game_qunitris.piece[0])
    start_y = game_qunitris.get_piece()[2]

    # This code generate all successors for right
    for i in range(start_y, 16 - piece_length):
        temp = deepcopy(game_qunitris)
        temp_s = ""
        for j in range(start_y, i):
            temp.right()
            temp_s += "m"
            cost = get_cost(temp,  combo)
            successor.append((temp, s + temp_s, cost))

    # This code generate all successors for left
    for i in range(start_y - 1, -1, -1):
        temp = deepcopy(game_qunitris)
        temp_s = ""
        for j in range(start_y, i, -1):
            temp.left()
            temp_s += "b"
        cost = get_cost(temp, combo)
        successor.append((temp, s + temp_s, cost))
    return successor


def rotate_piece_by_angle(game_qunitris, angle, s):
    assert angle in [90, 180, 270]
    temp = deepcopy(game_qunitris)
    for i in range(angle // 90):
        temp.rotate()
        s = s + "n"
        return (temp, s)
    


def get_successor(game_quintris, combo):
    successor = []
    s = ""
    successor = move_right_left(game_quintris, successor, s, combo)
    # Rotate
    angles = [90, 180, 270]
    for angle in angles:
        temp = rotate_piece_by_angle(game_quintris, angle, s)
        successor = move_right_left(temp[0], successor, temp[1], combo)
        
    temp_flip = deepcopy(game_quintris)
    temp_flip.hflip()
    s = "h"
    for angle in angles:
        temp = rotate_piece_by_angle(temp_flip, angle, s)
        successor = move_right_left(temp[0], successor, temp[1], combo)    
    
    
    
    
    return successor

# Python function to send the best successor
def get_best_successor(successor_list):
    return sorted(successor_list, key=lambda x: x[2])[0]


class ComputerPlayer:
    
    
    def __init__(self, combo):
        self.combo = combo
    # This function should generate a series of commands to move the piece into the "optimal"
    # position. The commands are a string of letters, where b and m represent left and right, respectively,
    # and n rotates. quintris is an object that lets you inspect the board, e.g.:
    #   - quintris.col, quintris.row have the current column and row of the upper-left corner of the 
    #     falling piece
    #   - quintris.get_piece() is the current piece, quintris.get_next_piece() is the next piece after that
    #   - quintris.left(), quintris.right(), quintris.down(), and quintris.rotate() can be called to actually
    #     issue game commands
    #   - quintris.get_board() returns the current state of the board, as a list of strings.
    #
    def get_moves(self, quintris):
        # super simple current algorithm: just randomly move left, right, and rotate a few times
        
        all_successors = get_successor(quintris, self.combo)
        best_child = get_best_successor(all_successors)
        return best_child[1]
        #return random.choice("mnbh") * random.randint(1, 10)
       
    # This is the version that's used by the animted version. This is really similar to get_moves,
    # except that it runs as a separate thread and you should access various methods and data in
    # the "quintris" object to control the movement. In particular:
    #   - quintris.col, quintris.row have the current column and row of the upper-left corner of the 
    #     falling piece
    #   - quintris.get_piece() is the current piece, quintris.get_next_piece() is the next piece after that
    #   - quintris.left(), quintris.right(), quintris.down(), and quintris.rotate() can be called to actually
    #     issue game commands
    #   - quintris.get_board() returns the current state of the board, as a list of strings.
    #
    def control_game(self, quintris):
        # another super simple algorithm: just move piece to the least-full column
        
        while 1:
            
            # column_heights = [ min([ r for r in range(len(board)-1, 0, -1) if board[r][c] == "x"  ] + [100,] ) for c in range(0, len(board[0]) ) ]
            # index = column_heights.index(max(column_heights))
            all_successors = get_successor(quintris)
            best_child = get_best_successor(all_successors)
            commands = best_child[1]
            
            for c in commands:
                time.sleep(0.1)                
                if c == 'b':
                    quintris.left()
                if c == 'm':
                    quintris.right()
                if c == 'n':
                    quintris.rotate()
            time.sleep(10)
            quintris.down()
                
                
            # if(index < quintris.col):
            #     quintris.left()
            # elif(index > quintris.col):
            #     quintris.right()
            # else:
            #     quintris.down()


###################
#### main program

(player_opt, interface_opt) = ("computer", "simple")#sys.argv[1:3]

final_scores = []
a = list(np.arange(3,7,1))
b = list(np.arange(1,6,1))
c = list(np.arange(-5, 0,1))
d = list(np.arange(1,3,1))
e = list(np.arange(1,3,1))

coefs = [a,b,c,d,e]

coefs_combo = list(itertools.product(*coefs))
combo1 = (6, 2, -4, 1, 2)

try:
    if player_opt == "human":
        player = HumanPlayer()
    elif player_opt == "computer":
        player = ComputerPlayer(combo1)
    else:
        print("unknown player!")

    if interface_opt == "simple":
        quintris = SimpleQuintris()
    elif interface_opt == "animated":
        quintris = AnimatedQuintris()
    else:
        print("unknown interface!")

    quintris.start_game(player)

except EndOfGame as s:
    

    print("\n\n\n", s)

# =============================================================================
# scoring_matrix = {}
# for i,combo in enumerate(coefs_combo):
#     
#     if i%10 == 0:
#         print(i, "remaiing iterations : ",  len(coefs_combo) - i)
#     
#     scoring_matrix[combo] = []    
#     
#     # print("new combo is ", combo)
#     for n in range(10):
#         try:
#             if player_opt == "human":
#                 player = HumanPlayer()
#             elif player_opt == "computer":
#                 player = ComputerPlayer(combo)
#             else:
#                 print("unknown player!")
#         
#             if interface_opt == "simple":
#                 quintris = SimpleQuintris()
#             elif interface_opt == "animated":
#                 quintris = AnimatedQuintris()
#             else:
#                 print("unknown interface!")
#         
#             quintris.start_game(player)
#         
#         except EndOfGame as s:
#             
#         
#             # print("\n\n\n", s)
#             scoring_matrix[combo].append(quintris.state[1])
#     
# # print(final_scores)
# with open('score.txt', 'w') as file:
#      file.write(json.dumps(scoring_matrix))
# =============================================================================
     
     
    
