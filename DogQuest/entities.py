import pygame as pg
from pygame.locals import *
from DogQuest import GAME_DIMENSIONS, FPS

import random
import sys

pg.init()

screen = pg.display.set_mode(GAME_DIMENSIONS)
pg.display.set_caption("DogQuest")

obstacles = []

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
        
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Rock:
    def __init__(self, x, y, vx, width, height):
        self.x = x
        self.y = y
        self.vx = vx
        self.width = width
        self.height = height
        self.hitbox = (x, y, width, height)

        self.image = pg.image.load("Resources/Images/rock.png").convert_alpha()
        self.rect = self.image.get_rect()

    def movement(self):
        if self.x >= GAME_DIMENSIONS[0]:
            self.vx = 0 
        else:
            self.x -= self.vx   

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Hole:
    def __init__(self, x, y, vx, width, height):
        self.x = x
        self.y = y
        self.vx = vx
        self.width = width
        self.height = height
        self.hitbox = (x, y, width, height)

        self.image = pg.image.load("Resources/Images/hole.png").convert_alpha()
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))        

class Cat:
    def __init__(self, x, y, vx, width, height):
        self.x = x
        self.y = y
        self.vx = vx
        self.width = width
        self.height = height
        self.hitbox = (x, y, width, height)

        self.image = pg.image.load("Resources/Images/cat.png").convert_alpha()
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Background:
    def __init__(self):

        self.image =pg.image.load("Resources/Images/grassbackground.png").convert_alpha()



class Game:
    def __init__(self):
        self.dog = Dog(50, 250, 0)

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


            screen.blit(self.background.image, (0, 0))
            self.dog.draw(screen)

            for obstacle in obstacles:
                obstacle.draw(screen)
                obstacle.x -= 1.4
                if obstacle.x < obstacle.width * -1:
                    obstacles.pop(obstacles.index(obstacle))

            pg.time.set_timer(USEREVENT+2, random.randrange(2000, 3500))
            if event.type == USEREVENT+2:
                r = random.randrange(0,100)
                if r == 0:
                    obstacles.append(Rock(750, random.randint(1, 550), 1, 50, 50))
                elif r == 1:
                    obstacles.append(Hole(750, random.randint(1, 550), 1, 50, 50))
                elif r == 2:
                    obstacles.append(Cat(750, random.randint(1, 550), 1, 50, 50))
                    
            

            pg.display.flip()