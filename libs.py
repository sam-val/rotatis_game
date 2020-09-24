import pygame as pg
import copy
import time
from collections import namedtuple

class MyRect:
    def __init__(self,pic = None, func = None, border_colour = None,
                 click_colour = None, line_colour = None, colour = None, rect=None ):
        self.func = func
        self.pic = pic
        self.click = False
        self.tick = 0
        self.border_colour = border_colour
        self.click_colour = click_colour
        self.line_colour = line_colour
        self.colour = colour
        self.rect = rect


class Board:
    LINE_WIDTH = 2
    def __init__(self, screen, x, y, width, height, cube_width, cube_height, rect, border = True, line=True):
        self.screen = screen
        self.posx = x
        self.posy = y
        self.w = width
        self.h = height
        self.border = border
        self.cube_w = cube_width
        self.cube_h = cube_height
        self.rect = rect
        self.array = self.make_new_array()
        self.line = line

    def draw_plain_init(self):
        for x in range(self.w):
            for y in range(self.h):
                px = self.posx + x*self.cube_w
                py = self.posy + y*self.cube_h
                border_colour = self.array[x +y * self.w].border_colour
                click = self.array[x+y*self.w].click
                # colour = self.array[x +y * self.w].click_colour if click else self.array[x+y*self.w].colour
                colour = self.array[x+y*self.w].colour

                pg.draw.rect(self.screen, colour, self.array[x+y*self.w].rect)
                # check and draw borders:
                # if x == 0 or x == self.w-1 or y == 0 or y == self.h-1:
                if self.checkIfBorder(x, y):
                    border_colour =  self.array[x+y*self.w].border_colour
                    if not border_colour:
                        border_colour = (0,0,0)
                    pg.draw.rect(self.screen, border_colour, self.array[x+y*self.w].rect)
                if self.line:
                    if self.array[x+y*self.w].line_colour:
                        # horizontal lines
                        pg.draw.line(self.screen, self.array[x+y*self.w].line_colour, (px, py), (px + self.cube_w, py))
                        if y == self.h-1:
                            pg.draw.line(self.screen, self.array[x+y*self.w].line_colour, (px,py+self.cube_h), (px+self.cube_w,py+self.cube_h))
                        # vertical lines
                        pg.draw.line(self.screen, self.array[x+y*self.w].line_colour, (px, py), (px, py + self.cube_h))
                        if x == self.w-1:
                            pg.draw.line(self.screen, self.array[x+y*self.w].line_colour, (px+self.cube_w,py), (px+self.cube_w,py+self.cube_h))


    def click(self,pos):
        for x in range(self.w):
            for y in range(self.h):
                Rect = self.array[x+y*self.w]
                if Rect.rect.collidepoint(pos):
                    Rect.click = not Rect.click
                    if not self.checkIfBorder(x,y):
                        if Rect.func is not None:
                            for i,f in enumerate(Rect.func):
                                Rect.func[i](currentRect=Rect, currentBoard=self)
                    return

    def checkIfBorder(self, x, y):
        if self.border:
            if x == 0 or x == self.w - 1 or y == 0 or y == self.h - 1:
                return True
        else:
            return False

    def make_new_array(self):
        array = [ None] * self.w * self.h
        for x in range(self.w):
            for y in range(self.h):
                px = self.posx + x*self.cube_w
                py = self.posy + y*self.cube_h
                array[x + y * self.w] = copy.copy(self.rect)
                array[x + y * self.w].rect = pg.Rect(px, py, self.cube_w, self.cube_h)
                if self.checkIfBorder(x, y):
                    array[x + y * self.w].func = None
                    array[x + y * self.w].border = True
        return array

    def init_array(self):
        self.array = self.make_new_array()

    def change_colour(self, colour):
        for x in range(self.w):
            for y in range(self.h):
               self.array[x+y*self.w].colour = colour



class Display:
    def __init__(self, surface, font=None, colour=None):
            self.surface = surface
            self.font = font
            self.colour = colour

    def display_text(self, x, y, text,
                     font=None,
                     colour=None, bg=None, centeredX = False, centeredY = False):
        if colour == None:
            colour = self.colour if self.colour != None else (0,0,0)
        if font == None:
            font = self.font if self.font != None else pg.font.SysFont("ubuntumono",20)
        text_w, text_h = font.size(text)
        text_sur = font.render(text, False, colour,bg)
        text_rect = text_sur.get_rect()

        self.display_sur(x, y, sur=text_sur, centeredY=centeredY, centeredX=centeredX)
        # self.surface.blit(text_sur,(x, y))

    def display_clock(self, x, y, secs=0, colour = None, font=None, bg = None, centeredX = False, centeredY=False):
        time = self.convert(secs=secs)

        self.display_text(x, y, text=time, colour=colour, font=font, bg=bg, centeredX=centeredX, centeredY=centeredY)

    @staticmethod
    def convert(secs = None):
        secs = int(secs)
        if secs < 0 or secs == None:
            secs = 0
        min = secs // 60
        sec = secs - min*60
        time = (str(min) if min > 9 else "0"+str(min)) + \
               ":" + \
               (str(sec) if sec > 9 else "0"+str(sec))
        return time


    def display_sur(self, x, y, sur, centeredX = False, centeredY = False):
        text_rect = sur.get_rect()
        text_w = sur.get_width()
        text_h = sur.get_height()

        if centeredX:
            x = x - text_w//2
        if centeredY:
            y = y - text_h//2

        self.surface.blit(sur, (x, y))

class FadeInEffect:
    def __init__(self,x=0,y=0,on = False,alpha =255,start_time = 0, first_start=True,still_time=1,text_colour=(0,0,0), text=""):
        self.text_colour = text_colour
        self.x= x
        self.y = y
        self.on = on
        self.alpha = alpha
        self.start_time = start_time
        self.first_start = first_start
        self.still_time = still_time
        self.text = text

    def update(self, colour = None,
               font = None, fading_speed=4, text=None):
        if font == None:
            print('no font!')
            return
        if text != None:
            self.text = text
        if colour != None:
            self.text_colour = colour
        if self.first_start:
            self.start_time = time.time()
            self.first_start = False

        original_sur = font.render(self.text, True, self.text_colour)
        text_sur = original_sur.copy()
        alpha_sur = pg.Surface(text_sur.get_size(), pg.SRCALPHA)
        t2 = time.time()
        if t2 - self.start_time > self.still_time:
            if self.alpha > 0:
                self.alpha = max(self.alpha - fading_speed, 0)
                text_sur = original_sur.copy()
                alpha_sur.fill((255, 255, 255, self.alpha))
                text_sur.blit(alpha_sur, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
            else:
                self.on = False
                self.alpha = 255
                self.first_start = True
                return
        self.text_sur = text_sur


