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
import random
import numpy
import time

from apps.fap import Fap
from apps.actions import Actions
from utils.colors import name_to_rgb
from copy import deepcopy

# from arbalet.core import Application, Rate
# import pygame

LEFT = (0, -1)
RIGHT = (0, 1)
DOWN = (1, 0)
UP = (-1, 0)


class Tetromino(object):
    types = {'i': [[1],
                   [1],
                   [1],
                   [1]],
             's': [[0, 2],
                   [2, 2],
                   [2, 0]],
             't': [[3, 0],
                   [3, 3],
                   [3, 0]],
             'o': [[4, 4],
                   [4, 4]],
             'l': [[5, 0],
                   [5, 0],
                   [5, 5]]}
    colors = ['black', 'cyan', 'green', 'deeppink', 'yellow', 'orangered']

    def __init__(self, px, py, height, width):
        self.type = random.choice(list(self.types.keys()))
        self.rotated = 0
        self.position = [px - len(self.get_value()) + 1, py]
        self.height = height
        self.width = width

    def update_position(self, x, y):
        self.position[0] = max(min(self.position[0] + x, self.height - 1), 0)
        self.position[1] = max(min(self.position[1] + y, self.width - len(self.get_value()[0])), 0)

    def rotate(self):
        if self.position[1] + len(self.get_value()) - 1 < self.width:
            self.rotated += 1

    def falldown(self):
        self.position = [self.position[0] + 1, self.position[1]]

    def get_value(self):
        return numpy.rot90(numpy.array(self.types[self.type], dtype=int), self.rotated)


class Tetris(Fap):
    PLAYABLE = True
    ACTIVATED = True

    PARAMS_LIST = {}

    def __init__(self):
        self.PARAMS_LIST = {'speed': 0.15}

        Fap.__init__(self)
        self.w_size = self.model.height
        self.h_size = self.model.width

        self.grid = numpy.zeros([self.h_size, self.w_size], dtype=int)
        self.old_grid = deepcopy(self.grid)
        self.speed = 2  # Speed of tetromino fall in Hertz
        self.score = 0
        self.playing = True
        self.tetromino = None
        self.command = {'left': False, 'right': False, 'down': False, 'rotate': False}  # User commands (joy/keyboard)
        self.touchdown = False  # True if the tetro has reached the floor


    def handle_message(self, data, path=None): # noqa
        new_dir = None
        self.command['rotate'] = False  # The rotate event cannot be extended
        self.command['down'] = False  # The rotate event cannot be extended
        self.command['right'] = False  # The rotate event cannot be extended
        self.command['left'] = False  # The rotate event cannot be extended

        if data == Actions.K_UP:
            self.command['rotate'] = True
        elif data == Actions.K_DOWN:
            self.command['down'] = True
        elif data == Actions.K_RIGHT:
            self.command['right'] = True
        elif data == Actions.K_LEFT:
            self.command['left'] = True

        if new_dir is not None:
            self.DIRECTION = new_dir
        """
        Sleep until the next step and process user events: game commands + exit
        Previous commands are kept into account and extended events (i.e. a key stayed pressed) are propagated
        :return: True if user asked to abort sleeping (accelerate or quit), False otherwise
        """
        changes_pending = self.command['left'] or self.command['right'] or self.command['rotate']
        if changes_pending:
            old_position = deepcopy(self.tetromino.position)
            self.tetromino.update_position(0, -1 if self.command['right'] else 1 if self.command['left'] else 0)
            if self.command['rotate']:
                self.rotate_current_tetro()

            self.old_grid_empty = deepcopy(self.grid)
            self.draw_tetromino()
            if self.touchdown and changes_pending:       # If touch is due to pending changes
                self.tetromino.position = old_position  # We cancel the last move left/right
                self.grid = self.old_grid_empty         # We remove the collisionning tetro
                # self.draw_tetromino()                   # And redraw
                self.touchdown = False                  # This is not a real touchdown, cancel it
            elif self.touchdown:                        # Touch down
                self.grid = self.old_grid_filled        # We restore the last pose of the tetro before touching down
            else:
                self.old_grid_filled = deepcopy(self.grid)
                self.update_view()
                self.grid = self.old_grid_empty

    def game_over(self):
        print("Game OVER")
        self.flash()
        # self.ws.send("GAME OVER! Score: {}".format(len(self.queue)), 'deeppink')
        self.set_pink()
        self.send_game_over()

    def process_extras(self, x=None, y=None):
        pass

    def rotate_current_tetro(self):
        """
        Before rotating the falling tetro we check whether this is possible with a drawing simulation
        """
        before_rotation = deepcopy(self.grid)
        self.tetromino.rotate()  # simulate drawing
        self.draw_tetromino()
        if self.touchdown:
            self.tetromino.rotate()  # If the rotation creates a collision, rotate again
        self.grid = before_rotation

    def check_level_up(self):
        if self.score / 25 + 1 >= self.speed:
            self.speed += 1
            text = "Level {}".format(self.speed - 1)
            print(text)
            # self.model.write(text, "navy")

    def draw_tetromino(self):
        self.touchdown = False
        for x, z in enumerate(self.tetromino.get_value()):
            for y, v in enumerate(z):
                px = int(x + self.tetromino.position[0])  # x-position of the pixel we are about to draw
                py = int(y + self.tetromino.position[1])  # y-position of the pixel we are about to draw

                before_world = px < 0
                in_world = not before_world and px < self.h_size  # and py < self.w_size

                touchdown = False
                if not before_world and not in_world:
                    touchdown = True
                elif in_world and self.grid[px][py] > 0 and v:
                    touchdown = True

                if touchdown:
                    self.touchdown = True
                    return
                elif in_world and self.grid[px][py] == 0:  # Don't overwrite a previous tetro and
                    self.grid[px][py] = v

    def wait_for_timeout_or_event(self, allow_events=True):
        t0 = time.time()
        while time.time() - t0 < 1. / self.speed:
            time.sleep(0.07)
            if allow_events and self.command['down']:
                return

    def check_and_delete_full_lines(self):
        """
        Browse the grid and check for full lines. If lines are found they are deleted.
        :return: The number of deleted lines
        """
        def __delete_line(line):
            for l in range(line, 1, -1):
                for w in range(self.w_size):
                    self.grid[l][w] = self.grid[l - 1][w]

        lines = []
        for h in range(self.h_size):
            full = True
            for w in range(self.w_size):
                if self.grid[h][w] == 0:
                    full = False
                    break
            if full:
                __delete_line(h)
                lines.append(h)
        return len(lines)

    def new_tetromino(self):
        """
        Brings a new tetromino in the scene and make it falling until touchdown
        :return: The number of steps before touchdown (1 step only = gameover)
        """
        self.command['down'] = False
        self.touchdown = False
        self.tetromino = Tetromino(0, self.w_size / 2, self.h_size, self.w_size)
        steps = 0
        while not self.touchdown:
            self.old_grid_empty = deepcopy(self.grid)
            self.draw_tetromino()
            if self.touchdown:
                self.grid = self.old_grid_filled
            else:
                self.old_grid_filled = deepcopy(self.grid)
                self.update_view()
                self.grid = self.old_grid_empty
                self.tetromino.falldown()
            self.wait_for_timeout_or_event(not self.touchdown)
            # In case of touchdown do not modify this tetro again
            # so we disable events
            steps += 1
        return steps

    def update_view(self):
        with self.model:
            for w in range(self.w_size):
                for h in range(self.h_size):
                    # self.model.set_pixel(h, w, Tetromino.colors[self.grid[h][w]])
                    # reversed for frontage
                    self.model.set_pixel(w, h, Tetromino.colors[self.grid[h][w]])
            self.send_model()

    def set_pink(self):
        rouge = name_to_rgb('deeppink')
        for i in range(0, 19):
            self.model.set_column(i, rouge)
        self.send_model()

    def run(self, params, expires_at=None):
        self.start_socket()

        if not params:
            params = {}
        self.params = params

        time.sleep(3)
        while self.playing:
            if self.new_tetromino() == 1:
                print("GAME OVER")
                print("You scored", self.score)
                break
                pass
            else:
                time.sleep(0.5)
                lines = self.check_and_delete_full_lines()
                won = lines * lines
                self.score += won
                if won > 0:
                    print("score:", self.score)
            self.check_level_up()
            self.send_model()
        # Game over
        # if self.score > 0:
        self.flash()
        self.game_over()
        self.send_close_app()
        exit()
        # self.model.write("GAME OVER! Score: {}, level {}".format(self.score, self.speed - 1), 'deeppink')
