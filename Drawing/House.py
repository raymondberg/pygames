__author__ = 'rberg'

## This script provides an EXTREMELY basic shell for drawing.
## This script is designed to get students drawing and playing with renders in PyGame

import os, sys
import pygame
from pygame.locals import *
import random, math
if not pygame.font: print('Warning: fonts disabled')
if not pygame.mixer: print('Warning: sound disabled')


width = 600
height = 400

pygame.init()

screen = pygame.display.set_mode((width, height))
#Draw board

max_grass_height = 100
min_grass_height = 20
grass_level_y = height * (3.0/4)
grass_width = 10

house_width = width / 2
house_height = height / 2
house_top = grass_level_y - house_height
house_left = width / 2 - house_width / 2
roof_left_tip = (house_left - width/8, house_top + height/8)
roof_right_tip = (house_left + house_width + width/8, house_top + height/8)
roof_top_tip = ((2*house_left + house_width) /2, house_top - height/4)

door_width = house_width / 3
door_height = house_height / 2
door_top = grass_level_y - door_height
door_left = 2 * house_width / 3 + house_left - door_width

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
    pygame.draw.rect(screen, Color("blue"), (0,0,width,height))
    pygame.draw.rect(screen, Color("red"), (house_left,house_top,house_width,house_height))
    pygame.draw.rect(screen, Color("green"), (0,grass_level_y,width,height-grass_level_y))
    pygame.draw.rect(screen, Color("black"), (door_left,door_top,door_width,door_height))

    pygame.draw.polygon(screen, Color("black"), (roof_left_tip, roof_right_tip, roof_top_tip))
    for grass_type in [1.0]:
        adjusted_max_grass_height = max(max_grass_height * grass_type, min_grass_height)
        adjusted_grass_width = max(grass_width * grass_type,2)
        for x in range(0-grass_width,width):
            grass_height = random.random()*(adjusted_max_grass_height - min_grass_height) + min_grass_height
            grass_top_y = grass_level_y - grass_height
            if grass_height > 2:
                pygame.draw.arc(screen,Color("green"),(x,grass_top_y,adjusted_grass_width,grass_height*2),0,1.5)

    pygame.display.flip()
    pygame.time.delay(40)

