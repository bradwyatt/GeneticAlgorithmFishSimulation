import pygame, os
from pygame.locals import *

class genmenu(object):

    def __init__(self, *items):

        self.menu = items
        self.x = 0
        self.y = 0
        self.font = pygame.font.SysFont('Arial',32)
        self.current = 0
        self.width = 1
        self.edges = 1
        self.default = (255,255,255) #default menu text is white
        self.choice = (0,255,0) #menu choice is green
        self.dist = len(self.menu)*self.font.get_height()
        for menuchoice in self.menu:
            msg = menuchoice[0] #what you read
            text = self.font.render(msg,self.edges,self.default) #render whilte font, smooth edges
            if text.get_width() > self.width:
                self.width = text.get_width()

    def position(self,x,y):
        self.x = x
        self.y = y

    def aliasing(self, val):
        if val == True:
            self.edges = 1
        else:
            self.edges = 0

    def center(self,x,y):
        self.x = x-(self.width)/2
        self.y = y-(self.width)/2

    def changeFont(self,font,size=32):
        self.font = pygame.font.Font(os.path.join('fonts', font),size)

    def defaultColor(self,color):
        self.default = color

    def choiceColor(self,color):
        self.choice = color

    def create(self,screen):
        select = 0
        for choice in self.menu:
            if select == self.current:
                color = self.choice
            else:
                color = self.default
            msg = choice[0]
            text = self.font.render(msg,self.edges,color)
            if text.get_width() > self.width:
                self.width = text.get_width()
            screen.blit(text, (self.x-(text.get_width()/2),self.y+(select*4*self.font.get_height()+5)))
            select += 1

    def choose(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.current += 1
                if event.key == pygame.K_UP:
                    self.current -= 1
                if event.key == pygame.K_RETURN:
                    self.menu[self.current][1]()
        if self.current > len(self.menu)-1:
            self.current = 0
        if self.current < 0:
            self.current = len(self.menu)-1