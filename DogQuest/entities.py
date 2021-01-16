import pygame as pg
from pygame.locals import *
from DogQuest import GAME_DIMENSIONS, FPS

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
        self.rect.y += self.vy
    

    def control(self):
        key_pressed = pg.key.get_pressed()
        if key_pressed[K_w]:
            self.rect.y = -10
        elif key_pressed[K_s]:
            self.rect.y = 10
        else:
            self.vy = 0



class Game:
    def __init__(self):
        self.screen = pg.display.set_mode(GAME_DIMENSIONS)
        pg.display.set_caption("DogQuest")

        self.dog = Dog(100, 100, 0)
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
            
            self.dog.update()

            self.dog.control()

            self.screen.fill((255, 0, 0))
            self.screen.blit(self.dog.image, (self.dog.x, self.dog.y))

            pg.display.flip()