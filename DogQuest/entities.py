import pygame as pg
from pygame.locals import *
from DogQuest import GAME_DIMENSIONS, FPS

import random
import sys

pg.init()

screen = pg.display.set_mode(GAME_DIMENSIONS)
pg.display.set_caption("DogQuest")

obstacles = []

class Dog(pg.sprite.Sprite):
    def __init__(self, x, y, vy):
        pg.sprite.Sprite.__init__(self)
        self.vy = vy

        self.dying = False

        self.image = pg.image.load("Resources/Images/dog.png").convert_alpha()
        self.rect = self.image.get_rect(x=x, y=y)
    

    def update(self):
        self.rect.y += self.vy

    def control(self):
        key_pressed = pg.key.get_pressed()
        if key_pressed[K_w]:
            self.vy = -10
            if self.rect.y <= 0:
                self.vy = 0
        elif key_pressed[K_s]:
            self.vy = 10
            if self.rect.y + 74 >= GAME_DIMENSIONS[1]:
                self.vy = 0
        else:
            self.vy = 0
        
    '''def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))'''
    
    '''def collision(self, obs):
        if self.rect.colliderect(obs.rect):
            return True'''

class Rock(pg.sprite.Sprite):
    def __init__(self, x, y, vx):
        pg.sprite.Sprite.__init__(self)
        self.vx = vx

        self.image = pg.image.load("Resources/Images/rock.png").convert_alpha()
        self.rect = self.image.get_rect(x=x, y=y)

    def movement(self):
        if self.rect.x >= GAME_DIMENSIONS[0]:
            self.vx = 0 
        else:
            self.rect.x -= self.vx   

    '''def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))'''

class Hole(pg.sprite.Sprite):
    def __init__(self, x, y, vx):
        pg.sprite.Sprite.__init__(self)
        self.vx = vx

        self.image = pg.image.load("Resources/Images/hole.png").convert_alpha()
        self.rect = self.image.get_rect(x=x, y=y)

    '''def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))'''        

class Cat(pg.sprite.Sprite):
    def __init__(self, x, y, vx):
        pg.sprite.Sprite.__init__(self)
        self.vx = vx

        self.image = pg.image.load("Resources/Images/cat.png").convert_alpha()
        self.rect = self.image.get_rect(x=x, y=y)

    '''def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))'''


class Background:
    def __init__(self):

        self.image =pg.image.load("Resources/Images/grassbackground.png").convert_alpha()



class Game:
    def __init__(self):
        self.dog = Dog(50, 250, 0)
        self.rock = Rock(750, random.randint(0, 550), 0)
        self.hole = Hole(750, random.randint(0, 550), 0)
        self.cat = Cat(750, random.randint(0, 550), 0)

        self.background = Background()

        self.player = pg.sprite.Group(self.dog)
        self.problems = pg.sprite.Group(self.rock, self.hole, self.cat)
        self.all = pg.sprite.Group(self.player, self.problems)

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


            screen.blit(self.background.image, (0, 0))
            self.player.draw(screen)

            '''self.dog.collision(Rock)
            if self.dog.dying == True:
                game_over = True'''
            
            '''for obstacle in self.problems:
                self.problems.draw(screen)
                self.problems.rect.x -= 1.4
                if self.problems.rect.x < 0:
                    self.problems.pop(obstacles.index(obstacle))'''

            pg.time.set_timer(USEREVENT, random.randrange(2000, 3500))
            if event.type == USEREVENT:
                r = random.randrange(0,100)
                if r == 0:
                    self.problems.draw(screen)
                elif r == 1:
                    self.problems.draw(screen)
                elif r == 2:
                    self.problems.draw(screen)

            pg.display.flip()