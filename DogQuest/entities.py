import pygame as pg
from pygame.locals import *
from DogQuest import GAME_DIMENSIONS, FPS, BLACK, WHITE

import random
import sys
import enum
import sqlite3
from sqlite3 import Error

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

input_box = []

DBFILE = 'highscore.db'
con = sqlite3.connect(DBFILE)
c = con.cursor()


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

        if key_pressed[K_SPACE]:
            pg.mixer.Sound.play(bark_sound)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def kill_animation_load(self):
        return [pg.image.load(f"Resources/Images/dogkill0{i}.png") for i in range(self.num_imgs_kill -1)]

    def kill(self, dt):
        if self.ix_kill >= len(self.image_kill):
            self.status = DogStatus.Killed
            self.ix_kill = 0
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

class TextBox(pg.sprite.Sprite):
    def __init__(self, x, y, w, h, text=""):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.rect = pg.Rect(x, y, w, h)

        self.color_inactive = pg.Color(BLACK)
        self.color_active = pg.Color(WHITE)
        self.color = self.color_inactive

        self.font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 35)
        self.text = text
        self.text_label = self.font.render(text, True, self.color)

        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pg.KEYDOWN and len(self.text) <= 12:
            if self.active:
                if event.key == pg.K_RETURN:
                    self.active = False
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.text_label = self.font.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.text_label.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.text_label, (self.rect.x + 5, self.rect.y + 5))
        pg.draw.rect(screen, (WHITE), self.rect, 2)

class StageStatus(enum.Enum):
    Running = 0
    Playingone = 1
    Playingtwo = 2
    Interlevels = 3
    GameOver = 4
    EndGame = 5
    Instructions = 6
    SubmitHighScore = 7
    HighScore = 8

class Game:
    def __init__(self):
        self.dog = Dog(50, 250, 0)
        self.pethouse = Pethouse(800, 200, -1)

        self.level = 1
        self.lives = 3
        self.score = 0

        self.stage = StageStatus.Running
    
        self.obs_passed = 0

        self.input_box = TextBox(300, 325, 600, 50)

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

        self.input_box.text = ""

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

            highscore_label = title_font.render("(H)igh Scores", 1, (BLACK))
            highscore_label_rect = highscore_label.get_rect(center = (200, 500))

            screen.blit(start_label, start_label_rect)
            screen.blit(instructions_label, instructions_label_rect)
            screen.blit(highscore_label, highscore_label_rect)

            self.score = 0
            self.text =""

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
                elif event.type == pg.KEYDOWN and event.key == pg.K_h:
                    self.stage = StageStatus.HighScore
                    self.highscore()
        
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
                elif event.type == pg.KEYDOWN and event.key == pg.K_s:
                    self.stage = StageStatus.SubmitHighScore
                    self.submit_highscore()
        
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
                elif event.type == pg.KEYDOWN and event.key == pg.K_s:
                    self.stage = StageStatus.SubmitHighScore
                    self.submit_highscore()
                    
            pg.display.flip()

    def submit_highscore(self):
        submit_hs_font_title =  pg.font.Font("Resources/Fonts/pixelfont.ttf", 35)
        submit_hs_font_misc = pg.font.Font("Resources/Fonts/pixelfont.ttf", 30)
        submit_hs_font_misc2 = pg.font.Font("Resources/Fonts/pixelfont.ttf", 25)

        self.clock.tick(FPS)

        while self.stage == StageStatus.SubmitHighScore:
            pg.Surface.fill(screen, BLACK)

            submit_hs_label = submit_hs_font_misc.render("Click below to ADD YOUR NAME", 1, (WHITE))
            submit_hs_label_rect = submit_hs_label.get_rect(center = (400, 250))

            misc_label1 = submit_hs_font_title.render("Thank you for playing", 1, (WHITE))
            misc_label1_rect = misc_label1.get_rect(center = (400, 100))
            
            misc_label2 = submit_hs_font_misc2.render("After writing the name, press return to submit", 1, (WHITE))
            misc_label2_rect = misc_label2.get_rect(center = (400, 500))

            misc_label3 = submit_hs_font_misc2.render("Press Space to see the high scores", 1, (WHITE))
            misc_label3_rect = misc_label3.get_rect(center = (400, 550))

            input_box = [self.input_box]

            screen.blit(submit_hs_label, submit_hs_label_rect)
            screen.blit(misc_label1, misc_label1_rect)
            screen.blit(misc_label2, misc_label2_rect)
            screen.blit(misc_label3, misc_label3_rect)

            if self.text != "" and self.input_box.active == False:
                input_box.clear()

            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    self.db_connection(DBFILE)
                    self.db_creation()
                    self.db_data_entry()
                    self.stage = StageStatus.HighScore
                    self.highscore()
                for box in input_box:
                    box.handle_event(event)
            for box in input_box:
                box.update()
                box.draw(screen)

            pg.display.flip()

    def highscore(self):
        hs_font = pg.font.Font("Resources/Fonts/pixelfont.ttf", 55)
        hs_font_data = pg.font.Font("Resources/Fonts/pixelfont.ttf", 35)
        hs_font_misc = pg.font.Font("Resources/Fonts/pixelfont.ttf", 25)

        self.clock.tick(FPS)

        entries = self.db_show_data()

        while self.stage == StageStatus.HighScore:
            pg.Surface.fill(screen, BLACK)

            hs_label = hs_font.render("HIGH SCORES", 1, (WHITE))
            hs_label_rect = hs_label.get_rect(center = (400, 100))

            hs_retry_label = hs_font_misc.render("Press return to restart the game", 1, (WHITE))
            hs_retry_label_rect = hs_retry_label.get_rect(center = (400, 550))
            
            data_entry_01_label = hs_font_data.render(str(entries[0]), 1, (WHITE))
            data_entry_01_label_rect = data_entry_01_label.get_rect(center = (400, 200))

            data_entry_02_label = hs_font_data.render(str(entries[1]), 1, (WHITE))
            data_entry_02_label_rect = data_entry_02_label.get_rect(center = (400, 250))

            data_entry_03_label = hs_font_data.render(str(entries[2]), 1, (WHITE))
            data_entry_03_label_rect = data_entry_03_label.get_rect(center = (400, 300))
            
            screen.blit(hs_label, hs_label_rect)
            screen.blit(hs_retry_label, hs_retry_label_rect)
            
            screen.blit(data_entry_01_label, data_entry_01_label_rect)
            screen.blit(data_entry_02_label, data_entry_02_label_rect)
            screen.blit(data_entry_03_label, data_entry_03_label_rect)
            
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.stage = StageStatus.Running
                    self.reset()
                    self.main_menu()
            
            pg.display.flip()
        pass

    def redraw_main(self):
        screen.blit(bg_img[1], (0, 0))
        lives_label = main_font.render(f"Lives: {self.lives}", 1, (WHITE))
        level_label = main_font.render(f"Level: {self.level}", 1, (WHITE))
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
            if self.dog.x >= 400 and self.dog.x + 10 <= 600:
                self.dog.angle += 1.5
                if self.dog.angle < 179:
                    self.dog.rotate(self.dog.angle)
                screen.blit(self.dog.rotated_dog, self.dog.rect)
            if self.obs_passed > 5:
                self.pethouse.draw(screen)
                self.pethouse.move(-5)

        if self.stage == StageStatus.Playingtwo:
            if self.dog.x >= 400 and self.dog.x + 10 <= 600:
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
                pg.mixer.Sound.play(kill_sound)
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
                pg.mixer.Sound.play(kill_sound)
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

            pg.display.flip() 

    def db_connection(self, db_file):
        con = None
        try:
            con = sqlite3.connect(db_file)
            return con
        except Error as error:
            print("Could not connect database: " + str(error))
        print("por aquí tira")

    def db_creation(self):
        try:
            c.execute('CREATE TABLE IF NOT EXISTS highscore (name TEXT, score INTEGER)')
            con.commit()
        except Error as error:
            print("Could not create table " + str(error))

    def db_data_entry(self):
        try:
            c.execute("INSERT INTO highscore (name, score) VALUES (?, ?)", (self.input_box.text, self.score))
            con.commit()
        except Error as error:
            print("Could not add data to database: " + str(error))

    def db_show_data(self):
        c.execute('SELECT * FROM highscore ORDER BY score DESC')
        entries = []
        for x in range(3):
            entries.append(c.fetchone())
        con.commit
        c.close

        return entries
    
    def db_close(self):
        c.close()
        con.close()



