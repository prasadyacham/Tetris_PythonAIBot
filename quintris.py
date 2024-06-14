# Simple quintris program! v0.2
# D. Crandall, Sept 2021
from copy import deepcopy

from AnimatedQuintris import *
from SimpleQuintris import *
from kbinput import *
import time, sys
import numpy as np


class HumanPlayer:
    def get_moves(self, quintris):
        print(
            "Type a sequence of moves using: \n  b for move left \n  m for move right \n  n for rotation\n  h for "
            "horizontal flip\nThen press enter. E.g.: bbbnn\n")
        moves = input()
        return moves

    def control_game(self, quintris):
        while 1:
            c = get_char_keyboard()
            commands = {"b": quintris.left, "h": quintris.hflip, "n": quintris.rotate, "m": quintris.right,
                        " ": quintris.down}
            commands[c]()


#####
# This is the part you'll want to modify!
# Replace our super simple algorithm with something better
# Inherited the idea of cost functions from
# "https://towardsdatascience.com/beating-#the-world-record-in-tetris-gb-with-genetics-algorithm-6c0b2f5ace9b"
# This function is responsible for associating a cost to each child nodes. The cost is associated by using
# column height, holes, bumps, pits and lines cleared functions. The column height gives the max of the col height
# on board. The holes provides how many holes are getting created for each child and same with pitscount and bumpiness.

def get_cost(game_quintris):
    temp = deepcopy(game_quintris)
    temp.down()
    temp_board = temp.get_board()

    boardlist = [[i for i in r] for r in temp_board]
    tlist = list(zip(*boardlist))
    cols_with_endx = [''.join(list(t) + ['x']).strip() for t in tlist]

    column_heights = [
        max([QuintrisGame.BOARD_HEIGHT - r for r in range(QuintrisGame.BOARD_HEIGHT - 1, 0, -1)
             if temp_board[r][c] == 'x'] + [0, ]) for c in range(QuintrisGame.BOARD_WIDTH)]

    max_height = max(column_heights)

    holes = sum([t.count(' ') for t in cols_with_endx])

    # Code to check if lines cleared
    linescleared = sum([1 if r.count("x") == QuintrisGame.BOARD_WIDTH else 0 for r in boardlist])

    # no of pits
    pitscount = sum([1 if t.count(" ") == QuintrisGame.BOARD_HEIGHT else 0 for t in tlist])

    bumpiness = [len(t) - 1 for t in cols_with_endx]
    bumpinesscount = sum([np.abs(i - j) for i, j in zip(bumpiness, bumpiness[1:])])

    # if max_height < 10:
    #     a = 20
    # else:
    #     a = 10

    return 10 * holes + 2 * bumpinesscount + 1 * pitscount + 2 * max_height - (40 * linescleared)


# This code is responsible for moving the child successors one right and one left and associating a
# cost function for each move after that child is placed down on board.

def move_right_left(game_qunitris, successor, s):
    piece_length = len(game_qunitris.piece[0])
    start_y = game_qunitris.get_piece()[2]

    # This code generate all successors for right
    for i in range(start_y, 16 - piece_length):
        temp = deepcopy(game_qunitris)
        temp_s = ""
        for j in range(start_y, i):
            temp.right()
            temp_s += "m"
        cost = get_cost(temp)
        successor.append((temp, s + temp_s, cost))

    # This code generate all successors for left
    for i in range(start_y - 1, -1, -1):
        temp = deepcopy(game_qunitris)
        temp_s = ""
        for j in range(start_y, i, -1):
            temp.left()
            temp_s += "b"
        cost = get_cost(temp)
        successor.append((temp, s + temp_s, cost))
    return successor


# This function is responsible for rotating the pieces and then calling the move right left function to
# perform the same steps as above.

def rotate_piece_by_angle(game_qunitris, angle, s):
    assert angle in [90, 180, 270]
    temp = deepcopy(game_qunitris)
    for i in range(angle // 90):
        temp.rotate()
        s = s + "n"
        return (temp, s)


# Successor function to send the child boards along with the cost of each board. This function
# calls right and left, rotate, hflip function and holds all the child nodes along with their cost.

def get_successor(game_quintris):
    successor = []
    s = ""
    successor = move_right_left(game_quintris, successor, s)

    # Rotate
    angles = [90, 180, 270]
    for angle in angles:
        temp = rotate_piece_by_angle(game_quintris, angle, s)
        successor = move_right_left(temp[0], successor, temp[1])

    ##################### HFLIP Code below ###################

    temp_flip = deepcopy(game_quintris)
    temp_flip.hflip()
    s = "h"
    # Added this line to generate the hflip child successors
    successor = move_right_left(temp_flip, successor, s)

    for angle in angles:
        temp = rotate_piece_by_angle(temp_flip, angle, s)
        successor = move_right_left(temp[0], successor, temp[1])

    # ##################### VFLIP Code below ###################
    #
    # temp_vflip = deepcopy(game_quintris)
    # temp_vflip.vflip()
    # s = "h"
    # # Added this line to generate the vflip child successors
    # successor = move_right_left(temp_vflip, successor, s)
    #
    # for angle in angles:
    #     temp = rotate_piece_by_angle(temp_vflip, angle, s)
    #     successor = move_right_left(temp[0], successor, temp[1])

    return successor


# Python function to send the best successor
def get_best_successor(successor_list):
    return sorted(successor_list, key=lambda x: x[2])[0]


class ComputerPlayer:
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

        all_successors = get_successor(quintris)
        best_child = get_best_successor(all_successors)
        return best_child[1]

        # return random.choice("mnbh") * random.randint(1, 10)

    # This is the version that's used by the animated version. This is really similar to get_moves,
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
            time.sleep(0.1)
            # time.sleep(3)
            all_successors = get_successor(quintris)
            best_child = get_best_successor(all_successors)
            commands = best_child[1]
            # print(commands)
            for c in commands:
                # time.sleep(0.1)
                if c == 'b':
                    quintris.left()
                elif c == 'm':
                    quintris.right()
                elif c == 'n':
                    quintris.rotate()
                elif c == 'h':
                    quintris.hflip()
            # quintris.down()


###################
#### main program

(player_opt, interface_opt) = sys.argv[1:3]

try:
    if player_opt == "human":
        player = HumanPlayer()
    elif player_opt == "computer":
        player = ComputerPlayer()
    else:
        print("unknown player!")

    if interface_opt == "simple":
        quintris = SimpleQuintris()
    elif interface_opt == "animated":
        quintris = AnimatedQuintris()
    else:
        print("unknown interface!")

    # for r in quintris.get_board() :
    #     print(r)

    quintris.start_game(player)

except EndOfGame as s:
    print("\n\n\n", s)
