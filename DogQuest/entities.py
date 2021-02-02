import pygame as pg
from pygame.locals import *
from DogQuest import GAME_DIMENSIONS, FPS, BLACK, WHITE
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
OBSROCKBIG = pg.image.load("Resources/Images/rockbig.png").convert_alpha()
OBSHOLE = pg.image.load("Resources/Images/hole.png").convert_alpha()
OBSCAT = pg.image.load("Resources/Images/cat.png").convert_alpha()
obstacles_img = [OBSROCK, OBSROCKBIG, OBSHOLE, OBSCAT]
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
        self.image_reversed = pg.image.load("Resources/Images/reversedog.png").convert_alpha()

        self.rect = self.image.get_rect(x=x, y=y)
        self.rect.x = self.x


    def reset(self):
        self.ix_kill = 0
        self.ticks_plus = 0
        self.status == DogStatus.Alive
        self.rect.x = self.x
        self.rect.y = self.y

        self.image = pg.image.load("Resources/Images/dog.png").convert_alpha()
    
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
        return [pg.image.load(f"Resources/Images/dogkill0{i}.png") for i in range(self.num_imgs_kill -1)]

    def kill(self, dt):
        if self.ix_kill >= len(self.image_kill):
            self.status = DogStatus.Killed
            return False

        self.image = self.image_kill[self.ix_kill]

        self.ticks_plus += dt
        if self.ticks_plus >= self.ticks_animation_frame:
            self.ix_kill += 1
            self.ticks_plus = 0

        return False
    
    def update_image(self, dt):
        self.update()

        if self.status == DogStatus.Dying:
            return self.kill(dt)

    def animation_finish(self):
        angle = 0
        if self.x < 700:
            self.x += 1.5
            self.y = self.y
            if self.y != 325:
                if self.y <= 324:
                    self.y += 1
                if self.y >= 326:
                    self.y += -1
            '''
            angle += 1
            self.image = pg.transform.rotate(self.image, angle)
            '''
        return True

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

class StageStatus(enum.Enum):
    Running = 0
    Playingone = 1
    Playingtwo = 2
    Interlevels = 3
    GameOver = 4

class Game:
    def __init__(self):
        self.dog = Dog(50, 250, 0)
        self.pethouse = Pethouse(800, 200, -1)

        self.level = 1
        self.lives = 3
        self.score = 0

        self.stage = StageStatus.Running
    
        self.obs_passed = 0

        self.clock = pg.time.Clock()

    def reset(self):
        self.dog.x = 50
        self.dog.y = 250
        self.dog.rect.x = self.dog.x
        self.dog.rect.y = self.dog.y

        self.dog.image = self.image = pg.image.load("Resources/Images/dog.png").convert_alpha()

        self.pethouse.x = 800
        self.pethouse.y = 200

        self.level = 1
        self.lives = 3
        self.score = 0

        self.stage = StageStatus.Running

        self.obs_passed = 0

        self.clock = pg.time.Clock()


    def main_menu(self):
        title_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 30)

        while self.stage == StageStatus.Running:
            self.clock.tick(FPS)

            screen.blit(bg_img[0], (0, 0))

            start_label = title_font.render("Press Return to start", 1, (BLACK))
            start_label_rect = start_label.get_rect(center = (200, 400))

            instructions_label = title_font.render("(I)nstructions", 1, (BLACK))
            instructions_label_rect = instructions_label.get_rect(center = (200, 450))

            screen.blit(start_label, start_label_rect)
            screen.blit(instructions_label, instructions_label_rect)

            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.reset()
                    self.stage = StageStatus.Playingone
                    self.levelone()
                elif event.type == pg.KEYDOWN and event.key == pg.K_i:
                    self.instructions()
        
                pg.display.flip()

    def instructions(self):
        pass

    def interlevels(self):
        interlevel_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 55)
        score_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 30)
        misc_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 15)

        self.clock.tick(FPS)

        while self.stage == StageStatus.Interlevels:
            pg.Surface.fill(screen, (BLACK))

            interlevel_label = interlevel_font.render("YOU DID IT", 1, (WHITE))
            interlevel_label_rect = interlevel_label.get_rect(center = (400, 300))

            score_label = score_font.render("Score: {}".format(self.score), 1, (WHITE))
            score_label_rect = score_label.get_rect(center = (400, 500))

            retry_label = misc_font.render("Press (R) to retry", 1, (WHITE))
            retry_label_rect = retry_label.get_rect(center = (100, 100))

            continue_label = misc_font.render("Press return to continue", 1, (WHITE))
            continue_label_rect = continue_label.get_rect(center = (700, 100))

            screen.blit(interlevel_label, interlevel_label_rect)
            screen.blit(score_label, score_label_rect)
            screen.blit(retry_label, retry_label_rect)
            screen.blit(continue_label, continue_label_rect)

            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_r:
                    self.stage = StageStatus.Running
                    self.main_menu()
                elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.reset()
                    self.stage = StageStatus.Playingtwo
                    self.leveltwo()
        
            pg.display.flip()

        
    def gameover(self):
        gameover_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 55)
        score_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 30)
        misc_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 15)

    
        self.clock.tick(FPS)

        while self.stage == StageStatus.GameOver:
            pg.Surface.fill(screen, (BLACK))

            gameover_label = gameover_font.render("GAME OVER", 1, (WHITE))
            gameover_label_rect = gameover_label.get_rect(center = (400, 300))

            score_label = score_font.render("Score: {}".format(self.score), 1, (WHITE))
            score_label_rect = score_label.get_rect(center = (400, 500))

            retry_label = misc_font.render("Press (R) to retry", 1, (WHITE))
            retry_label_rect = retry_label.get_rect(center = (100, 100))

            submit_label = misc_font.render("Press (S) to submit score", 1, (WHITE))
            submit_label_rect = submit_label.get_rect(center = (700, 100))

            screen.blit(gameover_label, gameover_label_rect)
            screen.blit(score_label, score_label_rect)
            screen.blit(retry_label, retry_label_rect)
            screen.blit(submit_label, submit_label_rect)

            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_r:
                    self.stage = StageStatus.Running
                    self.main_menu()
        
            pg.display.flip()


    def redraw_main(self):
        screen.blit(bg_img[1], (0, 0))
        lives_label = main_font.render(f"Lives: {self.lives}", 1, (WHITE))
        level_label = main_font.render(f"Nivel: {self.level}", 1, (WHITE))
        score_label = main_font.render(f"Score: {self.score}", 1, (WHITE))

        if self.stage == StageStatus.Playingone:
            if self.obs_passed < 10:    
                for obstacle in obstacles:
                    obstacle.draw(screen)
        if self.stage == StageStatus.Playingtwo:
            if self.obs_passed < 20:    
                for obstacle in obstacles:
                    obstacle.draw(screen)

        if self.dog.x < GAME_DIMENSIONS[0] - 99:
            self.dog.draw(screen)

        if self.dog.x == GAME_DIMENSIONS[0] - 99:
            screen.blit(self.dog.image_reversed, (545, 325))
        
        if self.stage == StageStatus.Playingone:
            if self.obs_passed > 5:
                self.pethouse.draw(screen)
                self.pethouse.move(-5)
        if self.stage == StageStatus.Playingtwo:
            if self.obs_passed > 10:
                self.pethouse.draw(screen)
                self.pethouse.move(-5)

        pg.draw.rect(screen, (0, 0, 0), (675, 480, 125, 125))
        screen.blit(lives_label, (GAME_DIMENSIONS[0] - 105, GAME_DIMENSIONS[1] - 50))
        screen.blit(level_label, (GAME_DIMENSIONS[0] - 105, GAME_DIMENSIONS[1] - 75))
        screen.blit(score_label, (GAME_DIMENSIONS[0] - 105, GAME_DIMENSIONS[1] - 100))

        pg.display.update()

    def levelone(self):

        while self.stage == StageStatus.Playingone:
            dt = self.clock.tick(FPS)

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
                self.dog.status = DogStatus.Dying

            if self.obs_passed == 10:
                self.dog.animation_finish()  

            if self.dog.x == GAME_DIMENSIONS[0] - 99:
                self.stage = StageStatus.Interlevels
                self.interlevels()


            events = pg.event.get()
            for event in events:
                key_pressed = pg.key.get_pressed()
                if event.type == pg.QUIT or key_pressed[K_ESCAPE]:
                    pg.quit()
                    sys.exit()
            
            self.dog.control()
            self.dog.update_image(dt)

            print(self.dog.status)

            self.redraw_main()

            pg.display.flip() 

    def leveltwo(self):
        self.level = 2
        self.score = 100

        while self.stage == StageStatus.Playingtwo:
            dt = self.clock.tick(FPS)

            wave_len = 23
            if len(obstacles) == 0:
                for i in range(wave_len):
                    obstacle = Obstacle(random.randrange(GAME_DIMENSIONS[0]+ 75, GAME_DIMENSIONS[0] + 850), random.randrange (0, GAME_DIMENSIONS[1] - 75), obs_vel)
                    obstacles.append(obstacle)

            
            for obstacle in obstacles:
                obstacle.move(obs_vel - 0.5)
                if self.obs_passed < 20:
                    if obstacle.x < 0:
                        obstacles.remove(obstacle)
                        self.obs_passed += 1
                        self.score += 10
                    if obstacle.rect.colliderect(self.dog.rect):
                        self.lives -= 1
                        obstacle.vx = 0
                        obstacles.remove(obstacle)
            
            if self.lives == 0:
                self.dog.status = DogStatus.Dying

            if self.obs_passed == 20:
                self.dog.animation_finish()  

            if self.dog.x == GAME_DIMENSIONS[0] - 99:
                self.stage = StageStatus.GameOver
                self.gameover()


            events = pg.event.get()
            for event in events:
                key_pressed = pg.key.get_pressed()
                if event.type == pg.QUIT or key_pressed[K_ESCAPE]:
                    pg.quit()
                    sys.exit()
            
            self.dog.control()
            self.dog.update_image(dt)

            self.redraw_main()

            pg.display.flip() 

#Tareas 
# Megaclase Obstacle - DONE
# Colisiones - Por qué no funcionan bien? - FUCKING DONE!
# Animación muerte perrete - DONE - Animación Final Nivel - Meterle rotación - rotozoom!?
# Método reiniciar para muerte perro
# Sonido muerte perrete
# Implementar niveles
# Reset juego al estar en game over
# Caseta final nivel - Compramos?
# Empezar a crear pantalla principal - Empezada, poco a poco - Compramos?

