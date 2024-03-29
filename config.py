# MIT License
#
# Copyright (c) 2019 Yurii Tolochko & Blanyal D'Souza.
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
"""Class to represent a configuration file."""


class CFG(object):
    """Represents a static configuration file used through the application.

    Attributes:
        num_iterations: Number of iterations.
        num_games: Number of self play games played during each iteration.
        num_mcts_sims: Number of MCTS simulations per game.
        c_puct: The level of exploration used in MCTS.
        l2_val: The level of L2 weight regularization used during training.
        momentum: Momentum Parameter for the momentum optimizer.
        learning_rate: Learning Rate for the momentum optimizer.
        t_policy_val: Value for policy prediction.
        temp_init: Initial Temperature parameter to control exploration.
        temp_final: Final Temperature parameter to control exploration.
        temp_thresh: Threshold where temperature init changes to final.
        epochs: Number of epochs during training.
        batch_size: Batch size for training.
        dirichlet_alpha: Alpha value for Dirichlet noise.
        epsilon: Value of epsilon for calculating Dirichlet noise.
        model_directory: Name of the directory to store models.
        num_eval_games: Number of self-play games to play for evaluation.
        eval_win_rate: Win rate needed to be the best model.
        load_model: Binary to initialize the network with the best model.
        human_play: Binary to play as a Human vs the AI.
        resnet_blocks: Number of residual blocks in the resnet.
        record_loss: Binary to record policy and value loss to a file.
        loss_file: Name of the file to record loss.
        game: Number of the game. 0: Blokus
    """
    num_iterations = 100
    num_games = 10
    num_mcts_sims = 20
    c_puct = 1
    l2_val = 0.0001
    momentum = 0.9
    learning_rate = 0.01
    t_policy_val = 0.0001
    temp_init = 1
    temp_final = 0.001
    temp_thresh = 10
    epochs = 30
    batch_size = 128
    dirichlet_alpha = 0.5
    epsilon = 0.25
    model_directory = "./blokus/models/"
    num_eval_games = 6
    eval_win_rate = 0.55
    load_model = 1
    human_play = 0
    resnet_blocks = 5
    record_loss = 1
    loss_file = "loss_new.txt"
    game = 2
