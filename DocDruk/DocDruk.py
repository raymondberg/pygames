__author__ = 'rberg'

import os, sys
import pygame
from pygame.locals import *
import time
import random
import math
if not pygame.font: print('Warning: fonts disabled')
if not pygame.mixer: print('Warning: sound disabled')

class DocDrukMain:
    """Main Class, initializes the game"""
    def __init__(self, width=640,height=480):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(Color("white"))

    def run(self):
        self.loadSprites()
        screenstop = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key in [K_RIGHT, K_LEFT, K_UP]:
                        self.docdruk.startmove(event.key)
                    if event.key == K_SPACE:
                        screenstop = not screenstop
                elif event.type == KEYUP:
                    if event.key in [K_RIGHT, K_LEFT, K_UP]:
                        self.docdruk.stopmove(event.key)
            #Screen
            if screenstop: continue
            self.screen.blit(self.background, (0, 0))
            self.docdruk.update()
            self.wm_sprites.draw(self.screen)
            pygame.display.flip()
            pygame.time.delay(10)

    def loadSprites(self):
        self.loadDocDruk()

    def loadDocDruk(self):
        try:
            self.docdruk.kill()
        except: pass
        #Snakes
        self.docdruk = DocDruk(self.width,self.height)
        self.wm_sprites = pygame.sprite.RenderPlain((self.docdruk))



class BergSprite(pygame.sprite.Sprite):
    def __init__(self,startX,startY):
        pygame.sprite.Sprite.__init__(self)
        self.startX = startX
        self.startY = startY
        self.image_loaded = False
    def load_image(self,name, colorkey=None):
        fullname = os.path.join("images",name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error as message:
            print('Cannot load image: ', name)
            raise
        image = image.convert()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey,RLEACCEL)
        self.image=image
        self.rect=image.get_rect()
        self.rect.move_ip(self.startX, self.startY)
        self.image_loaded = True

class BergGravSprite(BergSprite):
    GRAVITY_RATE_PIXELS_PSPS = 1 #Pixels per second, per second (rate of downward acceleration)
    UPDATE_CYCLE = .00
    TERMINAL_VELOCITY = 10
    def __init__(self,startX,startY,mass=1,gravityEffect=1):
        """
            Create Gravity Sprite that will naturally move in traditional fashion (down = earth)
        :return:
        """
        BergSprite.__init__(self,startX,startY)
        self.gravityEffect = gravityEffect
        self.mass = mass
        self.speed = 0
        self.in_air = True
        self.xMove = 0
        self.yMove = 0
        self.last_update = time.time()
        self.update_cycle = BergGravSprite.UPDATE_CYCLE

    def isMoving(self):
        return self.xMove != 0 or self.yMove != 0
    def getRightX(self):
        return self.rect.x + self.rect.width
    def getBottomY(self):
        return self.rect.y + self.rect.height

    def planMovement(self):
        if self.xMove != 0 or self.yMove != 0:
            localXMove = self.xMove + self.rect.x
            localYMove = self.yMove + self.rect.y
            return localXMove,localYMove
        return self.rect.x, self.rect.y

    def move(self,x,y):
        mytime = time.time()
        if self.in_air:
            self.yMove = min(BergGravSprite.GRAVITY_RATE_PIXELS_PSPS+self.yMove,self.TERMINAL_VELOCITY)
        if self.rect.x == x and self.rect.y == y: return
        localx = x - self.rect.x
        localy = y - self.rect.y
        self.rect.move_ip(localx, localy)
        if self.in_air:
            self.yMove = min(BergGravSprite.GRAVITY_RATE_PIXELS_PSPS+self.yMove,self.TERMINAL_VELOCITY)

        def update(self):
            '''
            Render the sprite in its new position (or leave as is)
            :return: null
            '''
            x,y = self.planMovement()
            self.move(x,y)


class DocDruk(BergGravSprite):
    X_DIST = 3
    Y_DIST = 15
    SAFE_DISTANCE = 175
    def __init__(self,maxX,maxY):
        BergGravSprite.__init__(self,0,0)
        self.maxX = maxX
        self.maxY = maxY
        self.load_image('snake_right.png',-1)
        self.xMove = 0
        self.yMove = 0

    def startmove(self,key):
        if (key == K_RIGHT): self.xMove = DocDruk.X_DIST
        elif (key == K_LEFT): self.xMove = -DocDruk.X_DIST
        elif (key == K_UP):
            self.yMove = -DocDruk.Y_DIST
            self.in_air = True

    def stopmove(self,key):
        if   (key == K_RIGHT): self.xMove = 0
        elif (key == K_LEFT): self.xMove = 0

    def update(self):
        x,y = self.planMovement()
        if self.rect.x + self.xMove < 0:
            x = 0
        elif self.getRightX() + self.xMove > self.maxX:
            x = self.maxX - self.rect.width
        if self.rect.y + self.yMove < 0:
            y = 0
        elif self.getBottomY() + self.yMove > self.maxY:
            y = self.maxY - self.rect.height
            self.in_air = False
        self.move(x,y)

def distance(tuple1,tuple2):
    return math.sqrt(math.pow(tuple1[0]-tuple2[0],2) + math.pow(tuple1[1]-tuple2[1],2))

if __name__ == "__main__":
    MainWindow = DocDrukMain()
    MainWindow.run()
