import os
# import pyglet
import pygame as pg
import time
from time import sleep
import cv2
from settings2 import *
from sprites2 import *
from moviepy.editor import VideoFileClip
from utils import VideoStream
vec = pg.math.Vector2


class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT)) # 창 크기
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.start_tick = 0
        self.game_tick = 0
        self.blink_index = 0
        self.blink_select = 0
        self.running = True # 게임 실행 Boolean 값
        self.practice = True # 연습 모드
        self.clear = False
        self.start = True
        self.ending = False
        self.load_data()
    
    def new(self):
        # start a new game
        self.hit_count = 0
        self.blink_data = list()     # data list
        self.blink_dataLen = 0       # data len

        self.all_sprites = pg.sprite.Group()
        self.blinks = pg.sprite.Group() # 깜빡임 지시자 sprite 그룹 생성
        self.timingbar = pg.sprite.Group()
        
        pg.mixer.music.load(os.path.join(self.snd_dir, 'old city theme.mp3')) #배경음 로드
        self.run()

    def run(self):
        self.start_tick = pg.time.get_ticks()
        self.load_blinkData()
        #game loop
        pg.mixer.music.play(loops=-1) #배경음 플레이 (loops 값 false = 반복, true = 한번)
        self.playing = True
        
        self.vs = VideoStream(device=0).start()
        while self.playing:
            self.clock.tick(FPS)
            self.update()
            self.draw()
            self.events()
                
        pg.mixer.music.fadeout(500) #배경음이 갑자기 꺼지지 않고 점점 꺼지게 함

    def update(self):
        #game loop - update
        self.all_sprites.update()
        self.game_tick = pg.time.get_ticks() - self.start_tick

        #게임 클리어 조건
        if self.hit_count == 8:
            self.clear_text()
            self.ending = True
            self.playing = False
            self.hit_count = 0
            sleep(1)

    def clear_text(self):
        for i in range(8):
            self.draw_text('잠금을 해제했습니다.', 60, GREEN, WIDTH/2, HEIGHT/2-100)
            pg.display.update()
            sleep(0.1)
            self.draw_text('잠금을 해제했습니다.', 60, YELLOW, WIDTH/2, HEIGHT/2-100)
            pg.display.update()
            sleep(0.1)

    def events(self):
        #game loop - events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                    self.running = False
                    self.start = False
                self.start = False
        
        self.create_blink()

    # 데이터를 불러오는 함수
    def load_data(self):
        self.dir = os.path.dirname(__file__)

        #image
        self.img_dir = os.path.join(self.dir, 'image2')
        self.bg_img = pg.image.load(os.path.join(self.img_dir, 'bg.png'))
        self.team_img = pg.image.load(os.path.join(self.img_dir, 'team.png'))
        self.end_img = pg.image.load(os.path.join(self.img_dir, 'ending.png'))
        self.eye_img = Spritesheet(os.path.join(self.img_dir, 'eye.png'))
        self.menu_select = pg.image.load(os.path.join(self.img_dir, 'menu_select.png'))

        self.font_name = pg.font.match_font(FONT_NAME) #FONT_NMAE과 맞는 폰트를 검색
        self.fnt_dir = os.path.join(self.dir, 'font')
        self.brankovic_font = os.path.join(self.fnt_dir, '경기천년바탕OTF_Regular.otf')

        #sound(효과음)
        self.snd_dir = os.path.join(self.dir, 'sound')
        self.jump_sound = pg.mixer.Sound(os.path.join(self.snd_dir, 'Jump.wav'))
        self.hit_sound = pg.mixer.Sound(os.path.join(self.snd_dir, 'Hit.wav'))
        self.game_over_sound = pg.mixer.Sound(os.path.join(self.snd_dir, 'Gameover.wav'))
        self.intro_effect = pg.mixer.Sound(os.path.join(self.snd_dir, 'intro_effect.wav'))

        ### blinking pattern
        self.blink_dir = os.path.join(self.dir, 'blinking')
        blink_lists = [i for i in os.listdir(self.blink_dir) if i.split('.')[-1] == 'ini']
        self.blink_list = list()         # 눈 깜빡임 패턴 파일 이름 리스트
        self.blink_path = list()         # 눈 깜빡임 패턴 파일 경로 리스트
        
        for blink in blink_lists:
            try:
                self.blink_list.append(blink.split('.')[0])
                self.blink_path.append(os.path.join(self.blink_dir, blink))
            except:
                print("error: " + str(blink) + "is unsupported format blinking pattern file.")

        self.pattern_num = len(self.blink_list)     # 패턴 수
        self.pattern_dataPath = list()                 # data file path list
        
        for blink in self.blink_list:
            self.pattern_dataPath.append(os.path.join(self.blink_dir, blink + ".ini"))

    def load_blinkData(self):
            with open(self.pattern_dataPath[self.blink_select - 1], "r", encoding = 'UTF-8') as data_file:
                data_fileLists = data_file.read().split('\n')
            
            current_blinkData = list()
            blink_s = list()
            for data_line in data_fileLists:
                if data_line != "" and data_line[0] != 's':
                    data_fileList = data_line.split(' - ')
                    time_list = data_fileList[0].split(':')
                    if data_fileList[1][0] != 'E':
                        blink_s = int(data_fileList[1])
                    else:
                        blink_s = -1
                    blink_t = int(time_list[0]) * 60000 + int(time_list[1]) * 1000 + int(time_list[2]) * 10
                        
                self.blink_data.append([blink_t, blink_s])
            print(self.blink_data)

    def draw(self):
        #game loop - draw
        frame = self.vs.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frame = pg.surfarray.make_surface(frame)
        self.screen.blit(frame, (0,0))
        circle = pg.draw.circle(self.screen, GREEN, (WIDTH/2, HEIGHT/2), WIDTH*0.01)
        self.draw_text("원이 화면의 중앙에 올 때 눈을 깜빡여주세요.", 22, BLACK, WIDTH/2, HEIGHT/5)
        pg.display.update()
        self.all_sprites.draw(self.screen)

###-------- start_screen 부분

    def start_new(self):
        self.start_group = pg.sprite.Group()
        self.select = Select(self)
        self.start_group.add(self.select)
        self.start_run()

    def start_run(self):
        #start loop
        self.start_playing = True
        while self.start_playing:
            self.clock.tick(FPS)
            self.start_events()
            self.start_update()
            self.start_draw()

    def start_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.start_playing:
                    self.start_playing = False
                self.start = False
            else:
                print ("a")

    def start_update(self):
        self.start_group.update()

    def start_draw(self):
        self.screen.blit(self.bg_img, (0,0))
        self.start_group.draw(self.screen)

        self.draw_text("눈 깜빡임 패턴으로 잠금 해제하기", 22, BLACK, WIDTH/2, HEIGHT/5)
        #self.draw_sprite(pos = , spr=)
        if self.select.select_number == 0:
            self.draw_text('연습', 40, BLACK, 198, 320)
            self.draw_text('실전', 36, GRAY, 302, 320)
            self.draw_text('EXIT', 36, GRAY, 440, 320)
        elif self.select.select_number == 1:
            self.draw_text('연습', 36, GRAY, 200, 320)
            self.draw_text('실전', 40, BLACK, 300, 320)
            self.draw_text('EXIT', 36, GRAY, 440, 320)
        elif self.select.select_number == 2:
            self.draw_text('연습', 36, GRAY, 200, 320)
            self.draw_text('실전', 36, GRAY, 302, 320)
            self.draw_text('EXIT', 40, BLACK, 438, 320)
        pg.display.update()

    def create_blink(self):
        if self.game_tick >= self.blink_data[self.blink_index][0]:
            if self.blink_data[self.blink_index][1] != -1:
                blink_num = len(self.blink_data[self.blink_index]) - 1
                
                for b in range(blink_num):
                    b_speed = self.blink_data[self.blink_index][b]
                    obj_b = Blink(self, b_speed)
                    self.all_sprites.add(obj_b)
                    self.blinks.add(obj_b)
                    
                self.blink_index += 1

###---------------end

    def show_over_screen(self):
        # Game Over시에 나타낼 스크린
        self.background = pg.Surface((WIDTH, HEIGHT))           #white background
        self.background = self.background.convert()
        surface = pg.Surface((WIDTH, HEIGHT))
        surface.fill(BLACK)
        self.screen.blit(self.background, (0,0))
        cv2.destroyAllWindows()
        self.draw_text("잠금을 해제하지 못했습니다.", 48, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text("Press 'Z' to retry, 'ESC' to 'QUIT'", 22, WHITE, WIDTH/2, HEIGHT*3/4)
        pg.display.update()
        self.wait_for_key2()
        sleep(1.5)

    #게임 클리어시 나타낼 화면
    def ending_screen(self):
        self.screen.blit(self.end_img, (0,0))
        pg.mixer.music.load(os.path.join(self.snd_dir, 'Ending.mp3'))
        pg.mixer.music.play(loops=-1)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH/2, HEIGHT - 400)
        self.draw_text("Press 'ESC' -> Menu", 20, WHITE, WIDTH/2, HEIGHT - 80)
        pg.display.update()
        self.wait_for_key()

    #START와 OVER스크린에서 화면대기 및 진행을 위한 메서드
    def wait_for_key(self):
        running = False
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    self.start = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False
                        waiting = False
                    if event.key == pg.K_z:
                        self.start = True
                        waiting = False

    def wait_for_key2(self):
        running = False
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    self.start = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        waiting = False
                        self.running = False

    #화면에 텍스트 처리를 위한 메서드
    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.brankovic_font, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)
        #render(text, antialias, color, background=None) -> Surface

    #밑줄 그어진 텍스트 처리
    def draw_text2(self, text, size, color, x, y):
        font = pg.font.Font(self.brankovic_font, size).set_underline(True)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)
    
    def draw_sprite(self, pos, spr, alpha = ALPHA_MAX):
            spr.set_alpha(alpha)
            self.screen.blit(spr, (round(pos[0]), round(pos[1])))

    #Intro
    def intro(self):
        screen_alpha = 1
        pg.mixer.music.load(os.path.join(self.snd_dir, 'Mysterious.ogg'))
        pg.mixer.music.play(loops=-1)
        while(screen_alpha <= ALPHA_MAX/2):
            self.draw_sprite((0,0), self.team_img, screen_alpha)
            screen_alpha += 1
            pg.display.update()
            sleep(0.02)
        pg.mixer.music.fadeout(200)
        sleep(0.2)
        self.running = True
        self.start = True

g = Game()
g.intro()
while g.start:
    if g.start:
        g.start_new()
    while g.running:
        g.new()
        if g.ending == True:
            g.ending_screen()
        else:
            g.show_over_screen()

pg.quit()
