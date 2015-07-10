__author__ = 'rberg'

## This script provides an EXTREMELY basic shell for tic-tac-toe without
## using any user-defined methods or classes, or any other advanced concepts.
## This script is designed to get students playing with game state and logic

import os, sys
import pygame
from pygame.locals import *
if not pygame.font: print 'Warning: fonts disabled'
if not pygame.mixer: print 'Warning: sound disabled'


width = 600
height = 600

pygame.init()

screen = pygame.display.set_mode((width, height))


x_turn = True;

#Draw board
line_width = 10
line_offset = line_width / 2
square_padding = 20
COLOR_WHITE = ((255,255,255))
COLOR_BLACK = ((0,0,0))
pygame.draw.rect(screen, COLOR_WHITE, (width*(1.0/3) - line_offset, line_offset, line_width, height-10))
pygame.draw.rect(screen, COLOR_WHITE, (width*(2.0/3) - line_offset, line_offset, line_width, height-10))
pygame.draw.rect(screen, COLOR_WHITE, (line_offset, height*(1.0/3) - line_offset, width - line_width, 10))
pygame.draw.rect(screen, COLOR_WHITE, (line_offset, height*(2.0/3) - line_offset, width - line_width, 10))

choices = [[None,None,None],[None,None,None],[None,None,None]]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            x = pos[0]
            y = pos[1]
            # Now you know what x and y are
            tridrent_x = x / (width/3)
            tridrent_y = y / (width/3)
            print( "%d, %d" % (tridrent_x, tridrent_y))
            if choices[tridrent_x][tridrent_y] is None:
                #now you know which square you are in
                left_x = tridrent_x * (width / 3) + square_padding
                top_y = tridrent_y * (height / 3) + square_padding
                right_x = left_x + width / 3 - 2*square_padding
                bottom_y = top_y + height / 3 - 2*square_padding
                #Now draw based on whose turn it is
                if x_turn:
                    pygame.draw.line(screen, COLOR_WHITE, (left_x,top_y),(right_x,bottom_y))
                    pygame.draw.line(screen, COLOR_WHITE, (left_x,bottom_y),(right_x,top_y))
                    choices[tridrent_x][tridrent_y] = "X"
                else:
                    center_x = (left_x + right_x ) / 2
                    center_y = (top_y + bottom_y ) / 2
                    radius_outside = (right_x-left_x) / 2
                    radius_inside = radius_outside - 1
                    pygame.draw.circle(screen, COLOR_WHITE, (center_x,center_y), radius_outside)
                    pygame.draw.circle(screen, COLOR_BLACK, (center_x,center_y), radius_inside)
                    choices[tridrent_x][tridrent_y] = "X"
                x_turn = not x_turn
    pygame.display.flip()

    # Figure out if the game is over
    moves_left = False
    for choice_row in choices:
        for choice in choice_row:
            if choice is None: 
                moves_left = True
    if moves_left:
        pygame.time.delay(50)
    else:
        choices = [[None,None,None],[None,None,None],[None,None,None]]
        pygame.time.delay(2000)
        pygame.draw.rect(screen, COLOR_BLACK, (0,0,width,height))
        pygame.draw.rect(screen, COLOR_WHITE, (width*(1.0/3) - line_offset, line_offset, line_width, height-10))
        pygame.draw.rect(screen, COLOR_WHITE, (width*(2.0/3) - line_offset, line_offset, line_width, height-10))
        pygame.draw.rect(screen, COLOR_WHITE, (line_offset, height*(1.0/3) - line_offset, width - line_width, 10))
        pygame.draw.rect(screen, COLOR_WHITE, (line_offset, height*(2.0/3) - line_offset, width - line_width, 10))
        pygame.display.flip()
        pygame.event.clear()

