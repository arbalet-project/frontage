#!/usr/bin/env python
"""
    Copyright 2016:
        Tomas Beati
        Maxime Carere
        Nicolas Verdier
    Copyright 2017:
        + Florian Boudinet
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html

    Arbalet - ARduino-BAsed LEd Table
    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import time

from apps.fap import Fap
from apps.actions import Actions
from utils.colors import name_to_rgb
from scheduler_state import SchedulerState

from random import randrange as rand
from time import sleep


# Define the shapes of the single parts
tetris_shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6]],

    [[7, 7],
     [7, 7]]
]


def rotate_clockwise(shape):
    return [[shape[y][x] for y in range(len(shape))] for x in range(len(shape[0]) - 1, -1, -1)]


def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[ cy + off_y ][ cx + off_x ]:
                    return True
            except IndexError:
                return True
    return False


def remove_row(board, row):
    del board[row]
    return [[0 for i in range(Tetris.cols)]] + board


def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy + off_y - 1][cx + off_x] += val
    return mat1


def new_board():
    board = [[0 for x in range(Tetris.cols)] for y in range(Tetris.rows)]
    return board


class Tetris(Fap):
    PLAYABLE = True
    ACTIVATED = True
    PARAMS_LIST = {}

    cols = 0
    rows = 0

    def __init__(self, username, userid):
        super(Tetris, self).__init__(username, userid)
        self.PARAMS_LIST = {'speed': 0.15}
        self.colors = ['black', 'deeppink', 'green', 'darkred', 'orangered', 'darkblue', 'cyan', 'yellow']
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        Tetris.cols = SchedulerState.get_rows()
        Tetris.rows = SchedulerState.get_cols()
        self.init_game()

    def new_stone(self):
        self.stone = self.next_stone[:]
        self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
        self.stone_x = int(Tetris.cols / 2 - len(self.stone[0])/2)
        self.stone_y = 0

        if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
            self.gameover = True

    def init_game(self):
        self.board = new_board()
        self.new_stone()
        self.level = 1.
        self.score = 0
        self.lines = 0

    def draw_matrix(self, matrix, offset):
        off_x, off_y  = offset
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val >0: self.model.set_pixel(x + off_x, y + off_y, name_to_rgb(self.colors[val]))

    def add_cl_lines(self, n):
        linescores = [0, 40, 100, 300, 1200]
        self.lines += n
        self.score += linescores[n] * self.level
        if self.lines >= self.level*6:
            self.level += 1

    def move(self, delta_x):
        if not self.gameover:
            new_x = self.stone_x + delta_x
            if new_x < 0:
                new_x = 0
            if new_x > Tetris.cols - len(self.stone[0]):
                new_x = Tetris.cols - len(self.stone[0])
            if not check_collision(self.board,
                                   self.stone,
                                   (new_x, self.stone_y)):
                self.stone_x = new_x

    def drop(self, manual):
        if not self.gameover:
            self.score += 1 if manual else 0
            self.stone_y += 1
            if check_collision(self.board,
                               self.stone,
                               (self.stone_x, self.stone_y)):
                self.board = join_matrixes(
                  self.board,
                  self.stone,
                  (self.stone_x, self.stone_y))
                self.new_stone()
                cleared_rows = 0
                while True:
                    for i, row in enumerate(self.board):
                        if 0 not in row:
                            self.board = remove_row(self.board, i)
                            cleared_rows += 1
                            break
                    else:
                        break
                if cleared_rows > 0:
                    self.send_message(Fap.CODE_TETRIS_CLEARED_ROW)
                self.add_cl_lines(cleared_rows)
                return True
        return False

    def insta_drop(self):
        if not self.gameover:
            while(not self.drop(True)):
                pass

    def rotate_stone(self):
        if not self.gameover:
            new_stone = rotate_clockwise(self.stone)
            if not check_collision(self.board,
                                   new_stone,
                                   (self.stone_x, self.stone_y)):
                self.stone = new_stone

    def start_game(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def handle_message(self, data, path=None):
        self.needs_update = True
        if data == Actions.K_UP:
            self.rotate_stone()
        elif data == Actions.K_DOWN:
            self.insta_drop()
        elif data == Actions.K_RIGHT:
            self.move(-1)
        elif data == Actions.K_LEFT:
            self.move(1)

    def update_and_sleep(self):
        self.needs_update = True
        for i in range(int(1 / (self.level * 0.05))):
            if self.needs_update:
                self.model.set_all('black')
                self.draw_matrix(self.board, (0, 0))
                self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
                self.send_model()
                self.needs_update = False
            sleep(0.05)

    def run(self, params, expires_at=None):
        self.start_socket()

        if not params:
            params = {}
        self.params = params

        self.gameover = False
        while not self.gameover:
            self.drop(False)
            self.update_and_sleep()

        self.send_game_over()
        time.sleep(1)
        self.flash()
        time.sleep(1)
        # self.send_close_app()
