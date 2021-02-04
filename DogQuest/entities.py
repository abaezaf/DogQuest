import pygame as pg
from pygame.locals import *
from DogQuest import GAME_DIMENSIONS, FPS, BLACK, WHITE
import random
import sys
import enum

pg.init()
pg.mixer.init()

pg.font.init()
main_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 20)

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

kill_sound = pg.mixer.Sound("Resources/Sounds/dogwhine.wav")
bark_sound = pg.mixer.Sound("Resources/Sounds/bark.wav")

current_time = 0
kill_time = 0


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

        self.angle = 0
        self.rotated_dog = self.image
        self.rotated_rect = self.rect

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

        if key_pressed[K_BACKSPACE]:
            pg.mixer.Sound.play(bark_sound)
                

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
        if self.x < 700:
            self.x += 2
            self.y = self.y
            if self.y != 325:
                if self.y <= 324:
                    self.y += 1
                if self.y >= 326:
                    self.y += -1
            self.rect.x = self.x
            self.rect.y = self.y

        return True

    def rotate(self, angle):
        self.rotated_dog = pg.transform.rotozoom(self.image, angle, 1)
        self.rotated_rect = self.rotated_dog.get_rect(center = self.rect.center)
        return self.rotated_dog, self.rotated_rect

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
    EndGame = 5
    Instructions = 6

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

        self.dog.image = pg.image.load("Resources/Images/dog.png").convert_alpha()

        self.dog.status = DogStatus.Alive

        self.pethouse.x = 800
        self.pethouse.y = 200

        self.level = 1
        self.lives = 3

        self.stage = StageStatus.Running

        obstacles = []

        current_time = 0
        kill_time = 0

        self.dog.angle = 0

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

            self.score = 0

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
                    self.stage = StageStatus.Instructions
                    self.instructions()

            print(f"ct: {current_time} kt:: {kill_time}")
        
            pg.display.flip()

    def instructions(self):
        instructionsmain_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 40)
        instructions_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 20)

        while self.stage == StageStatus.Instructions:
            self.clock.tick(FPS)

            screen.blit(bg_img[0], (0, 0))

            maintitle_label = instructionsmain_font.render("BE A GOOD BOY", 1, (BLACK))
            maintitle_label_rect = maintitle_label.get_rect(center = (250, 325))

            maintext_label = instructions_font.render("Press W and S to avoid obstacles and", 1, (BLACK))
            maintext_label_rect = maintext_label.get_rect(center = (250, 400))

            maintext_label2 = instructions_font.render("arrive as soon as possible to your pethouse!", 1, (BLACK))
            maintext_label2_rect = maintext_label2.get_rect(center = (250, 450))

            maintext_label3 = instructions_font.render("Press return to go back", 1, (BLACK))
            maintext_label3_rect = maintext_label3.get_rect(center = (250, 550))

            screen.blit(maintitle_label, maintitle_label_rect)
            screen.blit(maintext_label, maintext_label_rect)
            screen.blit(maintext_label2, maintext_label2_rect)
            screen.blit(maintext_label3, maintext_label3_rect)

            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.stage = StageStatus.Running
                    self.main_menu()

            pg.display.flip()

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
                    self.reset()
                    self.main_menu()
        
            pg.display.flip()

    def endgame(self):
        endgame_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 65)
        score_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 30)
        misc_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 15)

    
        self.clock.tick(FPS)

        while self.stage == StageStatus.EndGame:
            pg.Surface.fill(screen, (BLACK))

            endgame_label = endgame_font.render("CONGRATULATIONS", 1, (WHITE))
            endgame_label_rect = endgame_label.get_rect(center = (400, 300))

            score_label = score_font.render("Your final score: {}".format(self.score), 1, (WHITE))
            score_label_rect = score_label.get_rect(center = (400, 500))

            retry_label = misc_font.render("Press (R) to try again", 1, (WHITE))
            retry_label_rect = retry_label.get_rect(center = (100, 100))

            submit_label = misc_font.render("Press (S) to submit score", 1, (WHITE))
            submit_label_rect = submit_label.get_rect(center = (700, 100))

            screen.blit(endgame_label, endgame_label_rect)
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

        if self.dog.x < GAME_DIMENSIONS[0] - 400:
            self.dog.draw(screen)

        if self.stage == StageStatus.Playingone:
            if self.dog.x >= 400:
                self.dog.angle += 1.5
                if self.dog.angle < 179:
                    self.dog.rotate(self.dog.angle)
                screen.blit(self.dog.rotated_dog, self.dog.rect)
            if self.obs_passed > 5:
                self.pethouse.draw(screen)
                self.pethouse.move(-5)

        if self.stage == StageStatus.Playingtwo:
            if self.dog.x >= 400:
                self.dog.angle += 1.5
                if self.dog.angle < 179:
                    self.dog.rotate(self.dog.angle)
                screen.blit(self.dog.rotated_dog, self.dog.rect)
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
            kill_time = 0

            wave_len = 15
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
                if self.obs_passed == 10:
                    obstacles.clear()
            
            if self.lives == 0:
                self.dog.status = DogStatus.Dying
                #pg.mixer.Sound.play(kill_sound)
                obstacles.clear()

            if self.obs_passed == 10:
                self.dog.animation_finish()  

            if self.dog.x == GAME_DIMENSIONS[0] - 100:
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

            self.redraw_main()

            current_time = pg.time.get_ticks()

            if self.dog.status == DogStatus.Killed:
                kill_time = pg.time.get_ticks() + current_time

            if kill_time - current_time > 2000:
                self.stage = StageStatus.GameOver
                self.gameover()

            print(self.obs_passed)

            pg.display.flip() 

    def leveltwo(self):
        self.level = 2
        kill_time = 0

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
                if self.obs_passed == 20:
                    obstacles.clear()
            
            if self.lives == 0:
                self.dog.status = DogStatus.Dying
                #pg.mixer.Sound.play(kill_sound)
                obstacles.clear()

            if self.obs_passed == 20:
                self.dog.animation_finish()  

            if self.dog.x == GAME_DIMENSIONS[0] - 100:
                self.stage = StageStatus.EndGame
                self.endgame()


            events = pg.event.get()
            for event in events:
                key_pressed = pg.key.get_pressed()
                if event.type == pg.QUIT or key_pressed[K_ESCAPE]:
                    pg.quit()
                    sys.exit()
            
            self.dog.control()
            self.dog.update_image(dt)

            self.redraw_main()

            current_time = pg.time.get_ticks()

            if self.dog.status == DogStatus.Killed:
                kill_time = pg.time.get_ticks() + current_time

            if kill_time - current_time > 2000:
                self.stage = StageStatus.GameOver
                self.gameover()

            print(self.obs_passed)

            pg.display.flip() 

'''
Tareas

Quedan 2 cosas:

- Problema Reset - No funciona el timer al resetear - Se pierde animación muerte
- Sqlite y ponerse con los high scores y la base de datos

'''


