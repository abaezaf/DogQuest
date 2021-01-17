import pygame as pg
from pygame.locals import *
from DogQuest import GAME_DIMENSIONS, FPS

import random
import sys

pg.init()

class Dog:
    def __init__(self, x, y, vy):
        self.x = x
        self.y = y
        self.vy = vy

        self.image = pg.image.load("Resources/Images/dog.png").convert_alpha()
        self.rect = self.image.get_rect()
    

    def update(self):
        self.y += self.vy

    def control(self):
        key_pressed = pg.key.get_pressed()
        if key_pressed[K_w]:
            self.vy = -10
            if self.y <= 0:
                self.vy = 0
        elif key_pressed[K_s]:
            self.vy = 10
            if self.y + 74 >= GAME_DIMENSIONS[1]:
                self.vy = 0
        else:
            self.vy = 0

class Obstacle:
    def __init__(self, x, y, vx):
        self.x = x
        self.y = y
        self.vx = vx

        self.image = pg.image.load("Resources/Images/rock.png").convert_alpha()
        self.rect = self.image.get_rect()

class Background:
    def __init__(self):

        self.image =pg.image.load("Resources/Images/grassbackground.png").convert_alpha()



class Game:
    def __init__(self):
        self.screen = pg.display.set_mode(GAME_DIMENSIONS)
        pg.display.set_caption("DogQuest")

        self.dog = Dog(50, 250, 0)
        self.obstacle = Obstacle(400, 150, 20)
        self.background = Background()

        self.clock = pg.time.Clock()


    def main_loop(self):
        game_over = False

        while not game_over:
            self.clock.tick(FPS)

            events = pg.event.get()
            for event in events:
                key_pressed = pg.key.get_pressed()
                if event.type == pg.QUIT or key_pressed[K_ESCAPE]:
                    pg.quit()
                    sys.exit()
            
            self.dog.control()
            self.dog.update()

            self.screen.blit(self.background.image, (0, 0))
            self.screen.blit(self.dog.image, (self.dog.x, self.dog.y))
            self.screen.blit(self.obstacle.image, (self.obstacle.x, self.obstacle.y))

            pg.display.flip()