# MIT License
#
# Copyright (c) 2019 Yurii Tolochko.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

from copy import deepcopy
import numpy as np
import math
import random
import copy
from termcolor import colored


from game import Game

problematic = [line.strip() for line in open("problematic.txt", 'r')]
problematic = [int(x) for x in problematic]

class BlokusGame(Game):

    def __init__(self, n = 14):
        
        self.action_size = 17836
        self.problematic = problematic
        self.size = self.row = self.column = n 
        self.rounds = 0
        self.current_player = 1
        self.state = np.zeros((n,n), dtype = np.int8)
        self.pieces = {1: All_Shapes,
                      -1: All_Shapes
                        }
        self.score = {1: 0,
                      -1: 0}

        max_x = self.size - 1
        max_y = self.size - 1      
        self.corners = { 1: set([(4, 4)]), 
                        -1: set([(max_y -4, max_x-4)])
                        }
        
    def print_board(self):
        print(self.state)

    def colorBoard(self):
        n = 2
        """
        A bit of colour to check better.
        """
        print(' ' * n, end = ' ')
        for i in range(self.state.shape[1]):
            print(colored("{0:2d}".format(i+1), 'blue'), end = ' ')
        print(' ')
        for i, row in enumerate(self.state):
            print(colored("{0:2d}".format(i+1), 'blue'), end = ' ')
            for p, v in enumerate(row):
                if v == -1:
                    if p == len(row) -1:
                        print(colored("{0:2d}".format(v), 'green'))
                    else:
                        print(colored("{0:2d}".format(v),'green'), sep=' ', end= ' ', flush= True)
                elif v == 1:
                    if p == len(row) -1:
                        print(colored("{0:2d}".format(v), 'red'))
                    else:
                        print(colored("{0:2d}".format(v), 'red'), sep=' ', end= ' ', flush= True)
                
                # temporary just for visualizing move before accepting 
                elif v == 2:
                    if p == len(row) -1:
                        print("{0:2d}".format(v))
                    else:
                        print("{0:2d}".format(v), sep=' ', end= ' ', flush= True)

                elif v == 0:
                    if p == len(row) -1:
                        print("{0:2d}".format(v))
                    else:
                        print("{0:2d}".format(v), sep=' ', end= ' ', flush= True)


    def play_action(self, action):

        action = self.translate_action(action)
        # print(action.points)
        for (col, row) in action.points:
            self.state[col, row] = self.current_player
            self.score[self.current_player] += 1

        self.rounds += 1
        self.corners[self.current_player].update(self.update_corners(action))
        self.pieces[self.current_player] = self.remove_piece(action)
        self.corners[-self.current_player] = set([(i, j) for (i, j) in self.corners[-self.current_player] if self.state[i][j] == 0])

        self.current_player *= -1

    
    def get_valid_moves(self, current_player):

        all_moves = np.zeros(self.action_size, dtype = np.int8)
        list_of_legals = self.get_legal_moves(current_player)
        for i in list_of_legals:
            # get_legal_moves for some reason doesn't capture all illegal moves - adhoc solution is self.problematic
            if i not in self.problematic:
                all_moves[i] = 1


        return all_moves

    def check_game_over(self, current_player):
        # print('CHECKING GAME')
        moves = []
        for player in [1, -1]:
            moves.extend(self.get_valid_moves(player))
            if sum(moves) > 0:
                return False, 0

        if sum(moves) > 0:
            return False, 0
        elif self.score[current_player] >= self.score[-current_player]:
            return True, 1
        else:
            return True, -1

        return True, 0
    def remove_piece(self, piece):
        """
        Removes a given piece (Shape object) from the list of pieces a player has.
        """
        new_pieces = [s for s in self.pieces[self.current_player] if s.ID != piece.ID]
        return new_pieces   

    def update_corners(self, action):
        """
        Updates the available corners of a player.
        Placement should be in the form of a Shape object.
        """
        new_corners = set()
        for c in action.corners:
            if (self.in_bounds(c) and (not self.overlap([c]))):
                new_corners.add(c)
        return new_corners

    def in_bounds(self, point):
        """
        Takes in a tuple and checks if it is in the bounds of the board.
        """
        return (0 <= point[0] <= (self.size - 1)) & (0 <= point[1] <= (self.size - 1))

    def overlap(self, move):
        """
        Returns a boolean for whether a move is overlapping any pieces that have already been placed on the board.
        """
        if False in [(self.state[i][j] == 0) for (i, j) in move]:
            return True
        else:
            return False

    def corner(self, player_label, move):
        """
        Note: ONLY once a move has been checked for adjacency, this function returns a boolean; whether the move is
        cornering any pieces of the player proposing the move.
        """
        validates = []
        for (i, j) in move:
            if self.in_bounds((i + 1, j + 1,)):
                validates.append((self.state[i + 1][j + 1] == player_label))
            if self.in_bounds((i - 1, j - 1)):
                validates.append((self.state[i - 1][j - 1] == player_label))
            if self.in_bounds((i + 1, j - 1,)):
                validates.append((self.state[i + 1][j - 1] == player_label))
            if self.in_bounds((i - 1, j + 1)):
                validates.append((self.state[i - 1][j + 1] == player_label))
        if True in validates:
            return True
        else:
            return False

    def adj(self, player_label, move):
        """
        Checks if a move is adjacent to any squares on the board which are occupied by the player proposing the move
        and returns a boolean.
        """
        validates = []
        for (i, j) in move:
            if self.in_bounds((i + 1, j)):
                validates.append((self.state[i + 1][j] == player_label))
            if self.in_bounds((i - 1, j)):
                validates.append((self.state[i - 1][j] == player_label))
            if self.in_bounds((i, j - 1)):
                validates.append((self.state[i][j - 1] == player_label))
            if self.in_bounds((i, j + 1)):
                validates.append((self.state[i][j + 1] == player_label))
        if True in validates:
            return True
        else:
            return False

    def valid_move(self, action, player_label):
        if self.rounds < 2: # first actions haven't been done yet
            if ((False in [self.in_bounds(pt) for pt in action]) 
                or self.overlap(action) 
                or not (True in [(pt in self.corners[player_label]) for pt in action])):
                
                return False
            
            else:
                return True

        elif ((False in [self.in_bounds(pt) for pt in action])
              or self.overlap(action)
              or self.adj(player_label, action)
              or not self.corner(player_label, action)):
            return False

        else:
            return True

    def get_legal_moves(self, player_label):
        # print('WERE IN GET LEGAL MOVES')
        placements = []
        visited = []
        # Loop through every available corner.
        for cr in self.corners[player_label]:
            # Look through every piece offered. (This will be restricted according to certain algorithms.)
            for sh in self.pieces[player_label]:
                # Create a new shape so that the one in the player's list of shapes is not overwritten.
                try_out = copy.deepcopy(sh)
                # Loop over every potential refpt the piece could have.
                # for num in range(try_out.size):
                try_out.create(0, cr)
                # And every possible flip.
                for fl in try_out.flips:
                    temp_fl = copy.deepcopy(try_out)
                    temp_fl.flip(fl)
                    # And every possible orientation.
                    for rot in try_out.rots:
                        temp_rot = copy.deepcopy(temp_fl)
                        temp_rot.rotate(rot)
                        candidate = copy.deepcopy(temp_rot)
                        if fl == 'h':
                            f = 1
                        else:
                            f = 0
                        


                        if candidate.ID not in ['I5', 'I4','I3','I2']:
                            encoding = (cr[0] * 14 + cr[1]) * 91 + temp_rot.shift + (rot//90)*2 + f
                        else:
                            encoding = (cr[0] * 14 + cr[1]) * 91 + temp_rot.shift + (rot//90)*1 + f

                        if self.valid_move(candidate.points, player_label):
                            if not (set(candidate.points) in visited):
                                placements.append(encoding) 
                                visited.append(set(candidate.points))
        return placements


    def translate_action(self, input_number):
        position = input_number // 91
        input_number = input_number % 91
        if input_number < 8:
            piece = All_Shapes[0]
            rotation = input_number // 2
            fl = input_number % 2
        elif input_number < 16:
            piece = All_Shapes[1]
            rotation = (input_number % 8 )// 2
            fl = input_number % 2
        elif input_number < 24:
            piece = All_Shapes[2]
            rotation = (input_number % 8 )// 2
            fl = input_number % 2
        elif input_number < 32:
            piece = All_Shapes[3]
            rotation = (input_number % 8 )// 2
            fl = input_number % 2    
        elif input_number < 40:
            piece = All_Shapes[4]
            rotation = (input_number % 8 )// 2
            fl = input_number % 2
        elif input_number < 48:
            piece = All_Shapes[5]
            rotation = (input_number % 8 )// 2
            fl = input_number % 2
        elif input_number < 52:
            piece = All_Shapes[6]
            rotation = (input_number % 4 )// 2
            fl = input_number % 2
        elif input_number < 56:
            piece = All_Shapes[7]
            rotation = (input_number % 4 )// 2
            fl = input_number % 2
        elif input_number < 60:
            piece = All_Shapes[8]
            rotation = (input_number % 4 )// 2
            fl = input_number % 2
        elif input_number < 64:
            piece = All_Shapes[9]
            rotation = (input_number % 4 )// 2
            fl = input_number % 2
        elif input_number < 68:
            piece = All_Shapes[10]
            rotation = (input_number % 4 )// 2
            fl = input_number % 2
        elif input_number < 72:
            piece = All_Shapes[11]
            rotation = (input_number % 4 )// 2
            fl = input_number % 2
        elif input_number < 76:
            piece = All_Shapes[12]
            rotation = (input_number % 4 )// 2
            fl = input_number % 2
        elif input_number < 80:
            piece = All_Shapes[13]
            rotation = (input_number % 4 )// 2
            fl = input_number % 2
        elif input_number < 82:
            piece = All_Shapes[14]
            rotation = input_number % 2 
            fl = 0
        elif input_number < 84:
            piece = All_Shapes[15]
            rotation = input_number % 2 
            fl = 0
        elif input_number < 86:
            piece = All_Shapes[16]
            rotation = input_number % 2 
            fl = 0
        elif input_number < 88:
            piece = All_Shapes[17]
            rotation = 0 
            fl = 0
        elif input_number < 89:
            piece = All_Shapes[18]
            rotation = 0 
            fl = 0
        elif input_number < 90:
            piece = All_Shapes[19]
            rotation = 0 
            fl = 0
        elif input_number < 91:
            piece = All_Shapes[20]
            rotation = 0 
            fl = 0

        position_x = int(position // 14)
        position_y = position % 14
        if fl == 0: 
            fl = "None" 
        else: fl = "h"
        piece.create(0, (position_x, position_y))
        piece.flip(fl)
        piece.rotate(90 * rotation)
        
        return piece



def rotatex(coords, ref, deg):
    """
    Returns the new x value of a point (x, y) rotated about the point (refx, refy) by deg degrees clockwise.
    """
    x = coords[0]
    y = coords[1]
    refx = ref[0]
    refy = ref[1]
    return (math.cos(math.radians(deg))*(x - refx)) + (math.sin(math.radians(deg))*(y - refy)) + refx

def rotatey(coords, ref, deg):
    """
    Returns the new y value of a point (x, y) rotated about the point (refx, refy) by deg degrees clockwise.
    """
    x = coords[0]
    y = coords[1]
    refx = ref[0]
    refy = ref[1]
    return (- math.sin(math.radians(deg))*(x - refx)) + (math.cos(math.radians(deg))*(y - refy)) + refy

def rotatep(p, ref, d):
    """
    Returns the new point as an integer tuple of a point p (tuple) rotated about the point ref (tuple) by d degrees
    clockwise.
    """
    return (int(round(rotatex(p, ref, d))), int(round(rotatey(p, ref, d))))

class Shape(object):
    """
    A class that defines the functions associated with a shape.
    """

    def __init__(self):
        self.ID = "None"
        self.size = 1

      
    def create(self, num, pt):
        self.set_points(0, 0)
        pm = self.points
        self.points_map = pm
        self.refpt = pt
        x = pt[0] - self.points_map[num][0]
        y = pt[1] - self.points_map[num][1]
        self.set_points(x, y)

    def set_points(self, x, y):
        self.points = []
        self.corners = []

    def rotate(self, degrees):
        """
        Returns the points that would be covered by a shape that is rotated 0, 90, 180, of 270 degrees in a clockwise
        direction.
        """
        assert (self.points != "None")
        assert (degrees in [0, 90, 180, 270])

        def rotate_this(p):
            return (rotatep(p, self.refpt, degrees))

        self.points = list(map(rotate_this, self.points))
        self.corners = list(map(rotate_this, self.corners))

    def flip(self, orientation):
        """
        Returns the points that would be covered if the shape was flipped horizontally or vertically.
        """
        assert (orientation == "h" or orientation == "None")
        assert (self.points != "None")

        def flip_h(p):
            x1 = self.refpt[0]
            x2 = p[0]
            x1 = (x1 - (x2 - x1))
            return (x1, p[1])

        def no_flip(p):
            return p

        # flip the piece horizontally
        if orientation == "h":
            self.points = list(map(flip_h, self.points))
            self.corners = list(map(flip_h, self.corners))
        # flip the piece vertically
        elif orientation == "None":
            self.points = list(map(no_flip, self.points))
            self.corners = list(map(no_flip, self.corners))
        else:
            raise Exception("Invalid orientation.")

class I1(Shape):

    def __init__(self):
        self.ID = "I1"
        self.size = 1
        self.shift = 90
        self.flips = ['None']
        self.rots = [0]
    def set_points(self, x, y):
        self.points = [(x, y)]
        self.corners = [(x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1)]

class I2(Shape):

    def __init__(self):
        self.ID = "I2"
        self.size = 2
        self.shift = 86
        self.flips = ['None']
        self.rots = [0, 90]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1)]
        self.corners = [(x - 1, y - 1), (x + 1, y - 1), (x + 1, y + 2), (x - 1, y + 2)]

class I3(Shape):
    def __init__(self):
        self.ID = "I3"
        self.size = 3
        self.shift = 84
        self.flips = ['None']
        self.rots = [0, 90]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x, y + 2)]
        self.corners = [(x - 1, y - 1), (x + 1, y - 1), (x + 1, y + 3), (x - 1, y + 3)]

class I4(Shape):
    def __init__(self):
        self.ID = "I4"
        self.size = 4
        self.shift = 82
        self.flips = ['None']
        self.rots = [0, 90]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x, y + 2), (x, y + 3)]
        self.corners = [(x - 1, y - 1), (x + 1, y - 1), (x + 1, y + 4), (x - 1, y + 4)]

class I5(Shape):
    def __init__(self):
        self.ID = "I5"
        self.size = 5
        self.shift = 80
        self.flips = ['None']
        self.rots = [0, 90]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x, y + 2), (x, y + 3), (x, y + 4)]
        self.corners = [(x - 1, y - 1), (x + 1, y - 1), (x + 1, y + 5), (x - 1, y + 5)]

class V3(Shape):
    def __init__(self):
        self.ID = "V3"
        self.size = 3
        self.shift = 76
        self.flips = ['None', 'h']
        self.rots = [0, 90]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y)]
        self.corners = [(x - 1, y - 1), (x + 2, y - 1), (x + 2, y + 1), (x + 1, y + 2), (x - 1, y + 2)]

class L4(Shape):
    def __init__(self):
        self.ID = "L4"
        self.size = 4
        self.shift = 40
        self.flips = ['None', 'h']
        self.rots = [0, 90, 180, 270]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x, y + 2), (x + 1, y)]
        self.corners = [(x - 1, y - 1), (x + 2, y - 1), (x + 2, y + 1), (x + 1, y + 3), (x - 1, y + 3)]

class Z4(Shape):
    def __init__(self):
        self.ID = "Z4"
        self.size = 4
        self.shift = 68
        self.flips = ['None', 'h']
        self.rots = [0, 90]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y + 1), (x - 1, y)]
        self.corners = [(x - 2, y - 1), (x + 1, y - 1), (x + 2, y), (x + 2, y + 2), (x - 1, y + 2), (x - 2, y + 1)]

class O4(Shape):
    def __init__(self):
        self.ID = "O4"
        self.size = 4
        self.shift = 89
        self.flips = ['None']
        self.rots = [0]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y + 1), (x + 1, y)]
        self.corners = [(x - 1, y - 1), (x + 2, y - 1), (x + 2, y + 2), (x - 1, y + 2)]

class L5(Shape):
    def __init__(self):
        self.ID = "L5"
        self.size = 5
        self.shift = 8
        self.flips = ['None', 'h']
        self.rots = [0, 90, 180, 270]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y), (x + 2, y), (x + 3, y)]
        self.corners = [(x - 1, y - 1), (x + 4, y - 1), (x + 4, y + 1), (x + 1, y + 2), (x - 1, y + 2)]

class T5(Shape):
    def __init__(self):
        self.ID = "T5"
        self.size = 5
        self.shift = 56
        self.flips = ['None', 'h']
        self.rots = [0, 90]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x, y + 2), (x - 1, y), (x + 1, y)]
        self.corners = [(x + 2, y - 1), (x + 2, y + 1), (x + 1, y + 3), (x - 1, y + 3), (x - 2, y + 1), (x - 2, y - 1)]

class V5(Shape):
    def __init__(self):
        self.ID = "V5"
        self.size = 5
        self.shift = 52
        self.flips = ['None', 'h']
        self.rots = [0, 90]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x, y + 2), (x + 1, y), (x + 2, y)]
        self.corners = [(x - 1, y - 1), (x + 3, y - 1), (x + 3, y + 1), (x + 1, y + 3), (x - 1, y + 3)]

class N(Shape):
    def __init__(self):
        self.ID = "N"
        self.size = 5
        self.shift = 0 
        self.flips = ['None', 'h']
        self.rots = [0, 90, 180, 270]
    def set_points(self, x, y):
        self.points = [(x, y), (x + 1, y), (x + 2, y), (x, y - 1), (x - 1, y - 1)]
        self.corners = [(x + 1, y - 2), (x + 3, y - 1), (x + 3, y + 1), (x - 1, y + 1), (x - 2, y), (x - 2, y - 2)]

class Z5(Shape):
    def __init__(self):
        self.ID = "Z5"
        self.size = 5
        self.shift = 64
        self.flips = ['None', 'h']
        self.rots = [0, 90]
    def set_points(self, x, y):
        self.points = [(x, y), (x + 1, y), (x + 1, y + 1), (x - 1, y), (x - 1, y - 1)]
        self.corners = [(x + 2, y - 1), (x + 2, y + 2), (x, y + 2), (x - 2, y + 1), (x - 2, y - 2), (x, y - 2)]

class T4(Shape):
    def __init__(self):
        self.ID = "T4"
        self.size = 4
        self.shift = 48
        self.flips = ['None', 'h']
        self.rots = [0, 90]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y), (x - 1, y)]
        self.corners = [(x + 2, y - 1), (x + 2, y + 1), (x + 1, y + 2), (x - 1, y + 2), (x - 2, y + 1), (x - 2, y - 1)]

class P(Shape):
    def __init__(self):
        self.ID = "P"
        self.size = 5
        self.shift = 24
        self.flips = ['None', 'h']
        self.rots = [0, 90, 180, 270]
    def set_points(self, x, y):
        self.points = [(x, y), (x + 1, y), (x + 1, y - 1), (x, y - 1), (x, y - 2)]
        self.corners = [(x + 1, y - 3), (x + 2, y - 2), (x + 2, y + 1), (x - 1, y + 1), (x - 1, y - 3)]

class W(Shape):
    def __init__(self):
        self.ID = "W"
        self.size = 5
        self.shift = 72
        self.flips = ['None', 'h']
        self.rots = [0, 90]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y + 1), (x - 1, y), (x - 1, y - 1)]
        self.corners = [(x + 1, y - 1), (x + 2, y), (x + 2, y + 2), (x - 1, y + 2), (x - 2, y + 1), (x - 2, y - 2),
                        (x, y - 2)]

class U(Shape):
    def __init__(self):
        self.ID = "U"
        self.size = 5
        self.shift = 60
        self.flips = ['None', 'h']
        self.rots = [0, 90]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y + 1), (x, y - 1), (x + 1, y - 1)]
        self.corners = [(x + 2, y - 2), (x + 2, y), (x + 2, y + 2), (x - 1, y + 2), (x - 1, y - 2)]

class F(Shape):
    def __init__(self):
        self.ID = "F"
        self.size = 5
        self.shift = 32
        self.flips = ['None', 'h']
        self.rots = [0, 90, 180, 270]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y + 1), (x, y - 1), (x - 1, y)]
        self.corners = [(x + 1, y - 2), (x + 2, y), (x + 2, y + 2), (x - 1, y + 2), (x - 2, y + 1), (x - 2, y - 1),
                        (x - 1, y - 2)]

class X(Shape):
    def __init__(self):
        self.ID = "X"
        self.size = 5
        self.shift = 88
        self.flips = ['None']
        self.rots = [0]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
        self.corners = [(x + 1, y - 2), (x + 2, y - 1), (x + 2, y + 1), (x + 1, y + 2), (x - 1, y + 2), (x - 2, y + 1),
                        (x - 2, y - 1), (x - 1, y - 2)]

class Y(Shape):
    def __init__(self):
        self.ID = "Y"
        self.size = 5
        self.shift = 16
        self.flips = ['None', 'h']
        self.rots = [0, 90, 180, 270]
    def set_points(self, x, y):
        self.points = [(x, y), (x, y + 1), (x + 1, y), (x + 2, y), (x - 1, y)]
        self.corners = [(x + 3, y - 1), (x + 3, y + 1), (x + 1, y + 2), (x - 1, y + 2), (x - 2, y + 1), (x - 2, y - 1)]

All_Shapes = [N(), L5(), Y(), P(), F(), L4(), T4(), V5(), T5(), U(), Z5(), Z4(), W(), V3(), I5(), I4(), I3(), I2(), X(), O4(), I1()]
