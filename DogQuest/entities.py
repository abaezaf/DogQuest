import pygame as pg
from pygame.locals import *
from DogQuest import GAME_DIMENSIONS, FPS
import random
import sys

pg.font.init()
main_font = pg.font.SysFont("arial", 25)

pg.init()

screen = pg.display.set_mode(GAME_DIMENSIONS)
pg.display.set_caption("DogQuest")

OBSROCK = pg.image.load("Resources/Images/rock.png").convert_alpha()
OBSHOLE = pg.image.load("Resources/Images/hole.png").convert_alpha()
OBSCAT = pg.image.load("Resources/Images/cat.png").convert_alpha()
obstacles_img = [OBSROCK, OBSHOLE, OBSCAT]
obstacles = []
obs_vel = -1.4


class Dog:
    def __init__(self, x, y, vy):
        self.x = x
        self.y = y
        self.vy = vy

        self.kill = False

        self.image = pg.image.load("Resources/Images/dog.png").convert_alpha()
        self.rect = self.image.get_rect(x=x, y=y)
    
    def update(self):
        self.y += self.vy
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

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, x, y, vx):
        self.x = x
        self.y = y
        self.vx = vx

        self.image = random.choice(obstacles_img)
        self.rect = self.image.get_rect(x=self.x, y=self.y)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self, vx):
        self.x += vx
        self.rect.x += vx
    
    def collision(self, smt):
        return self.rect.colliderect(smt.rect)



class Background:
    def __init__(self):
        self.image =pg.image.load("Resources/Images/grassbackground.png").convert_alpha()

class Game:
    def __init__(self):
        self.dog = Dog(50, 250, 0)

        self.background = Background()

        self.level = 1
        self.lives = 3

        self.clock = pg.time.Clock()

    def main_menu(self):
        title_font = pg.font.SysFont("comicsans", 30)
        start = True

        while start:
            self.clock.tick(FPS)

            screen.blit(self.background.image, (0, 0))
            title_label = title_font.render("Presiona espacio para empezar", 1, (255, 255, 255))
            screen.blit(title_label, (GAME_DIMENSIONS[0]/2, title_label.get_width()/2))

            events = pg.event.get()
            for event in events:
                key_pressed = pg.key.get_pressed()
                if event.type == pg.QUIT or key_pressed[K_ESCAPE]:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.main_loop()
        
                pg.display.flip()


    def redraw_main(self):
        screen.blit(self.background.image, (0, 0))
        lives_label = main_font.render(f"Vidas: {self.lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Nivel: {self.level}", 1, (255, 255, 255))

        screen.blit(lives_label, (GAME_DIMENSIONS[0] - 100, GAME_DIMENSIONS[1] - 50))
        screen.blit(level_label, (GAME_DIMENSIONS[0] - 100, GAME_DIMENSIONS[1] - 75))

        for obstacle in obstacles:
            obstacle.draw(screen)

        self.dog.draw(screen)

        pg.display.update()

    def main_loop(self):
        game_over = False

        while not game_over:
            self.clock.tick(FPS)

            wave_len = 15
            if len(obstacles) == 0:
                for i in range(wave_len):
                    obstacle = Obstacle(random.randrange(GAME_DIMENSIONS[0]+ 75, GAME_DIMENSIONS[0] + 850), random.randrange (0, GAME_DIMENSIONS[1] - 75), obs_vel)
                    obstacles.append(obstacle)

            for obstacle in obstacles:
                obstacle.move(obs_vel)
                if obstacle.x < 0:
                    obstacles.remove(obstacle)
                if obstacle.collision(self.dog):
                    self.lives -=1
                    print("Colisión Detectada")

            events = pg.event.get()
            for event in events:
                key_pressed = pg.key.get_pressed()
                if event.type == pg.QUIT or key_pressed[K_ESCAPE]:
                    game_over = True
                    pg.quit()
                    sys.exit()
            
            self.dog.control()
            self.dog.update()

            self.redraw_main()

            print(self.dog.rect)

            pg.display.flip() 

#Tareas 
# Megaclase Obstacle - DONE
# Colisiones - Por qué no funcionan bien?
# Animación muerte perrete
# Sonido muerte perrete
# Empezar a crear pantalla principal - Empezada, poco a poco
