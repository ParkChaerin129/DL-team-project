#sprite classes for ploatform game
import pygame as pg
from time import sleep
from settings2 import *
vec = pg.math.Vector2

ALPHA_MAX = 225

#Menu Slect 클래스
class Select(pg.sprite.Sprite):

    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface((120,40))
        self.image.blit(self.game.menu_select, (0, 0))
        self.image.set_alpha(0)
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH - 70, HEIGHT - 340)
        self.select_number = 0

    def update(self):
        self.acc = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.select_number -= 1
            if self.select_number < 0:
                self.select_number = 2
            sleep(0.14)

        if keys[pg.K_RIGHT]:
            self.select_number += 1
            if self.select_number > 2:
                self.select_number = 0
            sleep(0.14)

        if keys[pg.K_z] and self.select_number == 0:
            self.game.start_playing = False
            self.game.practice = True

        if keys[pg.K_z] and self.select_number == 1:
            self.game.start_playing = False
            self.game.practice = False

        if keys[pg.K_z] and self.select_number == 2:
            pg.quit()
            quit()
        
        sleep(0.05)

class Blink(pg.sprite.Sprite):
    def __init__(self, game, speed):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.speed = speed
        self.alpha = ALPHA_MAX
        self.correct = 0
        self.image = self.game.eye_img.get_image(0, 0, 11, 20)
        
        self.touch_coord = (round(5 - self.image.get_width() / 2), round(- self.image.get_height() / 2))

        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = round(WIDTH / 2), round(HEIGHT / 2)
        self.rect.x += self.touch_coord[0]
        self.rect.y += self.touch_coord[1]
        
    def update(self):

        self.image.set_alpha(self.alpha)
        
        if self.alpha > 0:
            if self.correct == 1:
                self.alpha -= ALPHA_MAX / 5
            else:
                if self.correct == -1:
                    self.alpha -= ALPHA_MAX / 85
                self.rect.x += self.rect.x
                    

            if self.rect.x > WIDTH * 2 or self.rect.x < -WIDTH or self.rect.y > HEIGHT * 2 or self.rect.y < -HEIGHT:
                self.kill()
        else:
            self.kill()

        if self.correct == 0 and self.rect.x == WIDTH / 2:
            self.game.hit_count += 1
            self.correct = 1
            self.game.jump_sound.play()

#이미지 sheet 및 이미지 로드를 위한 클래스
class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

        """The returned Surface will contain the same color format,
        colorkey and alpha transparency as the file it came from.
        You will often want to call Surface.convert() with no arguments,
        to create a copy that will draw more quickly on the screen."""

    #불러온 이미지(self.spritesheet)를  (0,0)에 불러오며, 이미지의(x,y)부터 (width, height)까지 자르겠다.
    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0,0), (x, y, width, height))
        return image
