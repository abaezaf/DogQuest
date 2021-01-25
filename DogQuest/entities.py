import pygame as pg
from pygame.locals import *
from DogQuest import GAME_DIMENSIONS, FPS
import random
import sys
import enum

pg.font.init()
main_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 20)

pg.init()

screen = pg.display.set_mode(GAME_DIMENSIONS)
pg.display.set_caption("DogQuest")

GAMEBG = pg.image.load("Resources/Images/grassbackground.png").convert_alpha()
MENUBG = pg.image.load("Resources/Images/mainmenubackground.png").convert_alpha()
bg_img = [MENUBG, GAMEBG]

OBSROCK = pg.image.load("Resources/Images/rock.png").convert_alpha()
OBSHOLE = pg.image.load("Resources/Images/hole.png").convert_alpha()
OBSCAT = pg.image.load("Resources/Images/cat.png").convert_alpha()
obstacles_img = [OBSROCK, OBSHOLE, OBSCAT]
obstacles = []
obs_vel = -1.4

class DogStatus(enum.Enum):
    Alive = 0
    Dying = 1
    Killed = 2


class Dog(pg.sprite.Sprite):
    num_imgs_kill = 9
    anim_ret = 5

    def __init__(self, x, y, vy):
        pg.sprite.Sprite.__init__(self)

        self.x = x
        self.y = y
        self.vy = vy

        self.image_kill = self.kill_animation_load()
        self.ix_kill = 0
        self.refresh = 0
        self.ticks_plus = 0
        self.ticks_animation_frame = 1000//FPS * self.anim_ret

        self.status = DogStatus.Alive

        self.image = pg.image.load("Resources/Images/dog.png").convert_alpha()

        self.rect = self.image.get_rect(x=x, y=y)
        self.rect.x = self.x

    def reset(self):
        self.ix_kill = 0
        self.ticks_plus = 0
        self.status = DogStatus.Alive
        self.rect.x = self.x
        self.rect.y = self.y
    
    def update(self):
        if self.status == DogStatus.Dying:
            return

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

    def kill_animation_load(self):
        return [pg.image.load(f"Resources/Images/dogkill0{i}.png") for i in range(self.num_imgs_kill)]

    def kill(self, dt):
        if self.ix_kill >= len(self.num_imgs_kill):
            self.status = DogStatus.Killed
        
        self.image = self.image_kill[self.ix_kill]

        self.ticks_plus += dt
        if self.ticks_plus >= self.ticks_animation_frame:
            self.ix_kill += 1
            self.ticks_plus = 0
        
        return False
    
    def update_image(self):
        self.update()

        if self.status == DogStatus.Dying:
            return self.kill(dt)
        


class Obstacle(pg.sprite.Sprite):
    def __init__(self, x, y, vx):
        pg.sprite.Sprite.__init__(self)


        self.x = x
        self.y = y
        self.vx = vx

        self.image = random.choice(obstacles_img)
        self.rect = self.image.get_rect(x=self.x, y=self.y)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self, vx):
        self.rect.x = self.x
        self.x += vx


class Pethouse(pg.sprite.Sprite):
    def __init__(self, x, y, vx):
        pg.sprite.Sprite.__init__(self)

        self.x = x
        self.y = y
        self.vx = vx

        self.image = pg.image.load("Resources/Images/pethouse.png").convert_alpha()
        self.rect = self.image.get_rect(x=self.x, y=self.y)

    def move(self, vx):
        while self.x >= 600:
            self.x += vx

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Game:
    def __init__(self):
        self.dog = Dog(50, 250, 0)
        self.pethouse = Pethouse(800, 200, -1)

        self.level = 1
        self.lives = 3
        self.score = 0

        self.obs_passed = 0

        self.clock = pg.time.Clock()

    def main_menu(self):
        title_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 30)
        start = True

        while start:
            self.clock.tick(FPS)

            screen.blit(bg_img[0], (0, 0))
            title_label = title_font.render("Click to show respect", 1, (0, 0, 0))
            screen.blit(title_label, (125, 380))

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
        screen.blit(bg_img[1], (0, 0))
        lives_label = main_font.render(f"Vidas: {self.lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Nivel: {self.level}", 1, (255, 255, 255))
        score_label = main_font.render(f"Score: {self.score}", 1, (255, 255, 255))

        if self.obs_passed < 10:    
            for obstacle in obstacles:
                obstacle.draw(screen)
        
        if self.obs_passed > 5:
            self.pethouse.draw(screen)
            self.pethouse.move(-5)

        pg.draw.rect(screen, (0, 0, 0), (675, 480, 125, 125))
        screen.blit(lives_label, (GAME_DIMENSIONS[0] - 105, GAME_DIMENSIONS[1] - 50))
        screen.blit(level_label, (GAME_DIMENSIONS[0] - 105, GAME_DIMENSIONS[1] - 75))
        screen.blit(score_label, (GAME_DIMENSIONS[0] - 105, GAME_DIMENSIONS[1] - 100))

        self.dog.draw(screen)

        pg.display.update()

    def main_loop(self):
        game_over = False

        while not game_over:
            self.clock.tick(FPS)

            wave_len = 13
            if len(obstacles) == 0:
                for i in range(wave_len):
                    obstacle = Obstacle(random.randrange(GAME_DIMENSIONS[0]+ 75, GAME_DIMENSIONS[0] + 850), random.randrange (0, GAME_DIMENSIONS[1] - 75), obs_vel)
                    obstacles.append(obstacle)

            
            for obstacle in obstacles:
                obstacle.move(obs_vel)
                if self.obs_passed < 10:
                    if obstacle.x < 0:
                        obstacles.remove(obstacle)
                        self.obs_passed += 1
                        self.score += 10
                    if obstacle.rect.colliderect(self.dog.rect):
                        self.lives -= 1
                        obstacle.vx = 0
                        obstacles.remove(obstacle)
            
                if self.lives == 0:
                    self.dog.status == DogStatus.Dying


            events = pg.event.get()
            for event in events:
                key_pressed = pg.key.get_pressed()
                if event.type == pg.QUIT or key_pressed[K_ESCAPE]:
                    game_over = True
                    pg.quit()
                    sys.exit()
            
            self.dog.control()
            self.dog.update_image()

            print(self.dog.status)

            self.redraw_main()


            pg.display.flip() 

#Tareas 
# Megaclase Obstacle - DONE
# Colisiones - Por qué no funcionan bien? - FUCKING DONE!
# Animación muerte perrete - Animación Final Nivel
# Sonido muerte perrete
# Implemetar niveles
# Caseta final nivel - SORTA
# Empezar a crear pantalla principal - Empezada, poco a poco - Sorta

