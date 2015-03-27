__author__ = 'rberg'

import os, sys
import pygame
from pygame.locals import *
import random
import math
if not pygame.font: print 'Warning: fonts disabled'
if not pygame.mixer: print 'Warning: sound disabled'


class BergSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
    def load_image(self,name, colorkey=None):
        fullname = os.path.join("images",name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error, message:
            print 'Cannot load image: ', name
            raise SystemExit, message
        image = image.convert()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey,RLEACCEL)
        return image, image.get_rect()

class SineMain:
    """Main Class, initializes the game"""
    COLOR_WHITE = ((250, 250, 250))
    COLOR_BLACK = ((0, 0, 0))
    MAX_SCORE = 1000

    def __init__(self, width=640,height=480):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(SineMain.COLOR_WHITE)
        self.level = 0
        self.total_pellets = 0

    def run(self):
        self.loadSprites()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key in [K_RIGHT, K_LEFT, K_UP, K_DOWN]:
                        self.waveMachine.startmove(event.key)
                elif event.type == KEYUP:
                    if event.key in [K_RIGHT, K_LEFT, K_UP, K_DOWN]:
                        self.waveMachine.stopmove(event.key)
            #Screen
            self.screen.blit(self.background, (0, 0))
            self.waveMachine.update()
            if self.waveMachine.isMoving():
                self.ripple_sprites.add(Ripple(self.screen,self.waveMachine.rect.x,self.waveMachine.rect.y,self.width,self.height))
            self.ripple_sprites.update()
            self.wm_sprites.draw(self.screen)
            self.ripple_sprites.draw(self.screen)
           # print len(self.ripple_sprites.sprites())
            for sprite in self.ripple_sprites.sprites():
                if sprite.offScreen():
                    sprite.kill()
            pygame.display.flip()
            pygame.time.delay(10)

    def loadSprites(self):
        self.loadWaveMachine()
        self.ripple_sprites = pygame.sprite.Group()

    def loadWaveMachine(self):
        try:    self.waveMachine.kill()
        except: pass
        #Snakes
        self.waveMachine = WaveMachine(self.width,self.height)
        self.wm_sprites = pygame.sprite.RenderPlain((self.waveMachine))

class WaveMachine(BergSprite):
    X_DIST = 3
    Y_DIST = 3
    SAFE_DISTANCE = 175
    def __init__(self,maxX,maxY):
        BergSprite.__init__(self)
        self.maxX = maxX
        self.maxY = maxY
        self.image, self.rect = self.load_image('pixel.png',-1)
        self.pellets = 0
        self.xMove = 0
        self.yMove = 0

    def startmove(self,key):
        if   (key == K_RIGHT): self.xMove = WaveMachine.X_DIST
        elif (key == K_LEFT): self.xMove = -WaveMachine.X_DIST
        elif (key == K_DOWN): self.yMove = WaveMachine.Y_DIST
        elif (key == K_UP): self.yMove = -WaveMachine.Y_DIST

    def stopmove(self,key):
        if   (key == K_RIGHT): self.xMove = 0
        elif (key == K_LEFT): self.xMove = 0
        elif (key == K_DOWN): self.yMove = 0
        elif (key == K_UP): self.yMove = 0

    def isMoving(self):
        return self.xMove != 0 or self.yMove != 0
    def getRightX(self):
        return self.rect.x + self.rect.width
    def getBottomY(self):
        return self.rect.y + self.rect.height

    def update(self):
        if self.xMove != 0 or self.yMove != 0:
            localXMove = self.xMove
            localYMove = self.yMove
            if self.rect.x + self.xMove < 0 or self.getRightX() + self.xMove > self.maxX:
                localXMove = 0
            if self.rect.y + self.yMove < 0 or self.getBottomY() + self.yMove > self.maxY:
                localYMove = 0
            self.rect.move_ip(localXMove,localYMove)

def distance(tuple1,tuple2):
    return math.sqrt(math.pow(tuple1[0]-tuple2[0],2) + math.pow(tuple1[1]-tuple2[1],2))

class Ripple(BergSprite):
    MAX_RECTS = 50
    def __init__(self,screen,startX,startY,maxX,maxY):
        BergSprite.__init__(self)
        self.screen = screen
        self.startX = startX
        self.startY = startY
        self.maxX = maxX
        self.maxY = maxY
        self.index = 0
        self.image, self.rect = self.load_image('pixel.png',-1)
        self.rect.x = startX
        self.rect.y = startY
        self.rects = []
    def functionY(self,x):
        return int(20*math.sin(x/20.0))
    def functionRed(self,x):
        #print "Red %d" %  ((-int(math.sin(x/20.0)*100)+155))
        return (-int(math.sin(x/20.0)*100)+155)
    def functionBlue(self,x):
        #print "Blue %d" % (int(math.sin(x/20.0)*100)+155)
        return (int(math.sin(x/20.0)*100)+155)
    def functionGreen(self,x):
        return 0

    def update(self):
        x = self.index
        #print "drawing %d,%d  " % (x+self.startX,self.startY+self.functionY(x))
        self.rects.append([
                (self.functionRed(x),self.functionGreen(x),self.functionBlue(x)),
                pygame.Rect(x+self.startX,self.startY+self.functionY(x),1,1)
            ]
        )

        self.index += 1
        for rectangle in self.rects:
            pygame.draw.rect(self.screen,rectangle[0], rectangle[1],1)

        while len(self.rects) > Ripple.MAX_RECTS:
            self.rects.pop(0)
    def getRightX(self):
        return self.rect.x + self.rect.width
    def getBottomY(self):
        return self.rect.y + self.rect.height
    def offScreen(self):
        return self.startX + self.index > self.maxX

if __name__ == "__main__":
    MainWindow = SineMain()
    MainWindow.run()