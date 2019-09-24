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

from mcts import MonteCarloTreeSearch, TreeNode
from config import CFG

from copy import deepcopy


class Human_player():

    def __init__(self, game, net, human_player = 1):
        self.game = game
        self.net = net
        self.human_player = human_player

    @staticmethod
    def get_coords():
        
        coords = True
        while coords:
            try:
                coords = list(map(int, input("Please input a reference point (x,y) : ").split()))
                while len(coords) != 2:
                    coords = list(map(int, input("Please input a valid reference point (x,y): ").split()))
                else: return coords  
            except:
                print( "Invalid coordinate input.")
                coords = True
    
    def get_input(self, game):
        
        # get coordinates

        # choose piece
        if len(game.pieces[self.human_player]) > 0: 
            
            print('Select a piece from :')
            for i, piece in enumerate(game.pieces[self.human_player]):
                print(i, piece.ID) # , end = ''
            
            selected_ID = -1
            while selected_ID < 0 or selected_ID >= len(game.pieces[self.human_player]):
                try:
                    selected_ID  = int(input('Select a piece by its number'))
                except:
                    print('Invalid Value, try again')
        else:
            print('You have no pieces left')
            return None

        selected_piece = game.pieces[self.human_player][selected_ID]
        # choose reference point
        refpt = self.get_coords()
        flip, rot = -1, -1

        # choose flip
        while (flip != 0) and (flip != 1):
            flip = int(input('Do you want to flip? 1 or 0: '))

        # choose rotation
        while (rot != 0) and (rot != 1) and (rot != 2) and (rot != 3):
            rot = int(input('Which rotation? 0, 1, 2, 3 corresponds 0, 90, 180, 270 degrees: '))

        return selected_piece, refpt, rot, flip

    def play(self):

        mcts = MonteCarloTreeSearch(self.net)
        game = deepcopy(self.game)
        game_over = False
        value = 0
        node = TreeNode()
        valid = 0
        # self.game.colorBoard()
        game.print_board()

        while not game_over:
            
            if game.current_player == self.human_player:
                valid = False
                while valid == False: 
                    piece, refpt, rot, flip = self.get_input(game)
                    piece.create(0, (refpt[0], refpt[1]))

                    f = 'None'
                    if flip == 0:
                        f == 'None'
                    else:
                        f = 'h'

                    piece.flip(f)
                    piece.rotate(90*rot)

                    valid = game.valid_move(piece.points, self.human_player)
                    

                    if valid == False:
                        print('You selected an illegal move, please reselect')
                        # print('attempting', piece.points)
                        # print('corners are ', game.corners[self.human_player])

                    if piece.ID not in ['I5', 'I4','I3','I2']:
                        encoding = (refpt[0] * 14 + refpt[1]) * 91 + piece.shift + (rot//90)*2 + flip
                    else:
                        encoding = (refpt[0] * 14 + refpt[1]) * 91 + piece.shift + (rot//90)*1 + flip

                best_child = TreeNode()
                best_child.action = encoding
                print('CHOICE WAS MADE BY A HUMAN TO PLAY', piece.ID, '@', refpt)
            
            else:
                best_child = mcts.search(game, node, CFG.temp_final)

            action = best_child.action
            game.play_action(action)

            game.print_board()
            # game.colorBoard()

            game_over, value = game.check_game_over(game.current_player)

            best_child.parent = None
            node = best_child


        if value == self.human_player * game.current_player:
            print("You won!")
        elif value == -self.human_player * game.current_player:
            print("You lost.")
        else:
            print("Draw Match")
