__author__ = 'rberg'

import os, sys
import pygame
from pygame.locals import *
import random
import math
if not pygame.font: print 'Warning: fonts disabled'
if not pygame.mixer: print 'Warning: sound disabled'

class WormyMain:
    """Main Class, initializes the game"""
    DEFAULT_SQUARE_SIZE = 2
    MAX_ACTIVE_WORMS = 400

    def __init__(self, width=640,height=480,square_size=DEFAULT_SQUARE_SIZE):
        pygame.init()

        if width % square_size != 0 or height % square_size != 0 :
            raise Exception("Screen Width/Height must be evenly divisible by square size")
        self.screen = pygame.display.set_mode((width, height))
        self.grid = Grid(self.screen, width, height,square_size)
        self.worms = []

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    square = self.grid.square_from_position(pygame.mouse.get_pos())
                    self.addWorm(ColorWormy(self.grid,square))
            self.moveWorms()
            #Screen update
            pygame.display.flip()
            pygame.time.delay(10)

    def addWorm(self, worm):
        if worm is not None and len(self.worms) < self.MAX_ACTIVE_WORMS:
            self.worms.append(worm)

    def moveWorms(self):
        index = 0
        while index < len(self.worms):
            worm = self.worms[index]
            if worm.alive:
                worm.move()
                if worm.is_mature():
                    self.addWorm(worm.split())
                index += 1
            else: self.worms.pop(index)

class Wormy:
    def __init__(self, grid, square, mature_age=5):
        self.grid = grid
        self.x = square.x
        self.y = square.y
        self.mature_age = mature_age
        self.age = 0
        self.alive = True

    def forage(self):
        square = self.current_square()
        if self.alive:
            if self.finds_food(square):
                self.eat(square)
                self.age += 1
                return True
            else:
                self.alive = False
        return False

    def move(self):
        current_square = self.current_square()
        options = self.grid.adjacent_squares(current_square)
        random.shuffle(options)
        for option in options:
            if self.finds_food(option):
                self.set_square(option)
        self.forage()

    def eat(self,square):
        square.activate()

    def finds_food(self, square):
        return not square.active

    def current_square(self):
        return self.grid.square_from_index(self.x,self.y)

    def set_square(self, square):
        self.x = square.x
        self.y = square.y

    def is_mature(self):
        return self.age >= self.mature_age

    def copy_settings_into(self, worm):
        return worm

    def clone(self, square):
        return Wormy(self.grid,square)

    def split(self):
        self.age = 0
        options = self.grid.adjacent_squares(self.current_square())
        random.shuffle(options)
        for option in options:
            if self.finds_food(option):
                return self.clone(option)

class ColorWormy(Wormy):
    BLUE = ((50,50,200))
    BLACK = ((0,0,0))
    WHITE = ((250,250,250))
    RED = ((200,50,50))
    GREEN = ((50,200,50))
    COLORS = [RED, GREEN, BLUE, WHITE, BLACK]

    def color(self):
        try:
            return self.skin_color
        except:
            self.set_color(random.choice(ColorWormy.COLORS))
            return self.skin_color

    def set_color(self, color):
        self.skin_color = color

    def finds_food(self,square):
        return square.color != self.color()

    def clone(self,square):
        worm = ColorWormy(self.grid,square)
        worm.set_color(self.color())
        return worm

    def eat(self,square):
        square.set_color(self.color())

class Grid:
    def __init__(self, window, width, height, square_size=10,border=0):
        self.window = window
        self.square_size = square_size
        self.width = width
        self.height = height
        self.max_x = self.width / square_size
        self.max_y = self.height / square_size
        self.squares = []
        #Set up squares
        for y in range(0,self.max_y):
            self.squares.append([])
            for x in range(0,self.max_x):
                square = Square(self.window, x*self.square_size, y*self.square_size, self.square_size)
                square.set_index(x,y)
                self.squares[y].append(square)

    def square_from_position(self, position):
        if not self.position_in_range(position):   raise Exception("Out of range position (%d,%d)" % position)
        pointX = position[0]
        pointY = position[1]
        indexX = int(pointX / self.square_size)
        indexY = int(pointY / self.square_size)
        return self.square_from_index(indexX, indexY)

    def square_from_index(self, x, y):
        return self.squares[y][x]

    def adjacent_squares(self, square):
        options = []
        for i in range(square.y-1, square.y+2):
            for j in range(square.x-1, square.x+2):
                if (i != square.y or j != square.x) and self.index_in_range(j,i):
                    #if i == square.y or j == square.x: #only orthogonal, comment to allow diagonal
                        options.append(self.square_from_index(j,i))
        return options

    def index_in_range(self, x, y):
        return x >= 0 and y >= 0 and y < self.max_y and x < self.max_x

    def position_in_range(self, position):
        pointX = position[0]
        pointY = position[1]
        return pointX >= 0 and pointX <= self.width and pointY >= 0 and pointY <= self.height

class Square:
    COLOR_INACTIVE = ((250, 250, 250))
    COLOR_ACTIVE = ((0, 0, 200))

    def __init__(self, surface, x, y, size):
        self.posX = x
        self.posY = y
        self.size = size
        self.surface = surface
        self.active = False
        self.deactivate()

    def set_index(self, x, y):
        self.x = x
        self.y = y

    def deactivate(self):
        self.active = False
        self.set_color(self.COLOR_INACTIVE)

    def activate(self):
        self.active = True
        self.set_color(self.COLOR_ACTIVE)

    def toggle(self):
        if self.active: self.deactivate()
        else: self.activate()

    def set_color(self, color):
        self.color = color
        self.draw()

    def draw(self):
        pygame.draw.rect(self.surface, self.color, (self.posX, self.posY, self.size, self.size))

if __name__ == "__main__":
    MainWindow = WormyMain()
    MainWindow.run()
