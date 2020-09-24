from libs import Board, MyRect, Display, FadeInEffect
import pygame
import copy
import random
from collections import namedtuple
import time
from tkinter import messagebox as mb
import tkinter
from tkinter import ttk
import pickle
from pathlib import Path
from datetime import datetime
import os
from PIL import Image, ImageTk

# GLOBAL/SETTING VARIABLES:
BOARD_W = 6
BOARD_H = 6
SCREEN_WIDTH = 9
SCREEN_HEIGHT = 8
MENU_W = 3
MENU_H = 6
FRAME_RATE = 30
TITLE = "Rotatis"
CUBE_WIDTH = 100
PLAYTER_TIME = 60
DEFAULT_LEVEL = 0
RECORDS_PATH = "./.records.pickle"


CLOCK_POS_X = SCREEN_WIDTH - 1
CLOCK_POS_Y = 0.5


# settings
Settings = namedtuple('Settings', 'shapes_num moves_num time_reward')
normal = Settings(shapes_num=1, moves_num=3, time_reward=20)
easy = Settings(shapes_num=1, moves_num=2, time_reward=30)
hard = Settings(shapes_num=2, moves_num=4, time_reward=10)

Score = namedtuple("Score", "name difficulty level time_spent time_stamp")

DIFFICULTY_SETTINGS = {'easy':easy, 'normal': normal, 'hard': hard}

## COLOURS:
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 26, 0)
BRIGHT_RED = (170,1,20)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
BEIGE = (250, 175, 0)
AQUA = (128, 206, 207)
DARK_GREY = (64, 64, 64)
YELLOW = (255, 204, 0)
PURPLE = (148,0,211)
ORANGE = (255,106,2)
INDIGO = (75,0,130)
VIOLET = (238,130,238)
PINK = (231,84,128)
BROWN = (102,51,0)
CYAN = 0,173,238
SHAPE_COLOUR = ORANGE
CLICK_BUTTON_COLOUR = PINK
SIDE_SHAPE_COLOUR = ORANGE

#functions:

def checkBoard(*args, **kwargs):
    global swear_fade_ob
    global remaining_time
    global display
    global result_board_array
    global difficulty
    global currentSettings
    global swear_fade_ob
    global result_text_fade_ob
    if result_board_array == []:
        print("result board is empty")
        return
    def ridBorders(board):
        b = []
        for y in range(board.h):
            for x in range(board.w):
                if not board.checkIfBorder(x, y):
                    ob = board.array[x + y * board.w]
                    b.append(ob)
        return b

    b2 = ridBorders(field)
    b1 = result_board_array
    print('board b2')
    print_board(b2)
    print('board b1')
    print_board(b1)



    if compareShapes(b1, b2):
        ## if correct:
        remaining_time += currentSettings['current_time_reward']
        check_current_level(remaining_time) ## adjust current level
        set_settings() ## adjust settings
        set_puzzle(currentSettings)
        time_reward_fade_ob.on = True
        display = "correct"
        if not result_text_fade_ob.on:
            result_text_fade_ob.on = True
        result_text_fade_ob.first_start = True
    else:
        if not result_text_fade_ob.on:
            result_text_fade_ob.on=True
        result_text_fade_ob.first_start = True
        display = "WRONG!"

        if not swear_fade_ob.on:
            swear_fade_ob.on = True
        swear_fade_ob.first_start = True
        swear_adj = random.choice(adjs_cleaned)
        swear_noun = random.choice(nouns_cleaned)

        swear_fade_ob.text = swear_adj + " " + swear_noun
        swear_fade_ob.text = swear_fade_ob.text.capitalize() + "!!!"
        swear_fade_ob.x  = random.randint(0, CUBE_WIDTH * (SCREEN_WIDTH-3))
        swear_fade_ob.y = random.randint(0,CUBE_WIDTH * (SCREEN_HEIGHT-2))


def compareShapes(b1,b2):
    if (len(b1) != len(b2)):
        return False

    for x,y in zip(b1,b2):
       pair = x.click,y.click
       if pair != (True,True) and pair != (False,False):
           return False
    return True


def makeRandomShape(settings):
    global side_field
    global difficulty
    side_field.init_array()
    cubes = side_field.array
    rans = []
    chooseRandomElement(settings['current_shapes_num'], cubes, rans)
    for r in rans:
        r.colour = SIDE_SHAPE_COLOUR
        r.click = True

    print("side field after random():")
    print_board(side_field.array)
    global result_board_array
    result_board_array = copy.deepcopy(side_field.array)

def turnRandom(settings):
    global difficulty
    global result_board_array
    commands = []
    for _ in range(settings['current_moves_num']):
        command = random.choice(list(turn_commands.keys()))
        commands.append(command)
        move(command=command)

    print(commands)
    return commands

def chooseRandomElement(n, l, result_l):
    import random
    for i in range(n):
        if len(result_l) == n:
            return
        r = random.choice(l)
        if r not in result_l:
            result_l.append(r)
        else:
            chooseRandomElement(n, l, result_l)
            return

def fade_text(state, alpha, start_time, start,staying_still_time,text, x , y,
              colour=ORANGE, centeredY = False, centeredX=False,
              font = None, fading_speed=4):
    if font == None:
        print('no font!')
        return
    if globals()[start]:
        globals()[start_time] = time.time()
        globals()[start] = False

    original_sur = font.render(text, True, colour)
    text_sur = original_sur.copy()
    alpha_sur = pygame.Surface(text_sur.get_size(), pygame.SRCALPHA)
    t2 = time.time()
    if t2 - globals()[start_time] > globals()[staying_still_time]:
        if globals()[alpha] > 0:
            globals()[alpha] = max(globals()[alpha] - fading_speed, 0)
            text_sur = original_sur.copy()
            alpha_sur.fill((255, 255, 255, globals()[alpha]))
            text_sur.blit(alpha_sur, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            globals()[state] = False
            globals()[alpha] = 255
            globals()[start] = True
            return
    # animation loop:
    display_ob.display_sur(x, y, sur=text_sur, centeredX=centeredX, centeredY=centeredY)

def exit_game(*args, **kwargs):
    global running
    if confirmBox("Quitting game", "Are you sure, dear?"):
        running = False

def pause_game(*args, **kwargs):
    global paused
    global side
    paused = not paused
    print('game is','paused' if paused else 'resumed')

    if not paused:

        print('reset the puzzle')
        set_puzzle(currentSettings)

def change_colour_wrapper(to_colour, from_colour):
    def change_colour(*args, **kwargs):
        rect = kwargs['currentRect']
        board = kwargs['currentBoard']
        if rect.click:
            if to_colour:
                rect.colour = to_colour
            else:
                rect.colour = SHAPE_COLOUR
        else:
            if from_colour:
                rect.colour = from_colour
            else:
                rect.colour = DARK_GREY

    return change_colour

def move(command):
    # pass in the non bordered board
     # 0,1,2,3 is rotate left, rotate right, flip honrizontally, flip vertically respectively
    global side_field
    global result_board_array
    board = side_field
    shapes = []
    if command in turn_commands:
        print('move: ', command)
        for x in range(board.w):
            for y in range(board.h):
                cur_pos = x+y*board.w
                rect = result_board_array[cur_pos]
                if rect.click:
                    changed_pos = None
                    if command == 'left':
                        changed_pos = (board.w*(board.h-1)) - board.w*x + y
                    elif command == 'right':
                        changed_pos = (board.w-1) + board.w*x - y
                    elif command == 'horizontal':
                        changed_pos = (board.w-1) - x + y*board.w
                    elif command == 'vertical':
                        changed_pos = (board.w*(board.h-1)) + x - y*board.w

                    shapes.append(changed_pos)

    result_board_array = side_field.make_new_array()
    for i in shapes:
        result_board_array[i].colour = SIDE_SHAPE_COLOUR
        result_board_array[i].click = True
    print_board(result_board_array)

def print_board(board):
    global side_field
    for y in range(side_field.h):
        for x in range(side_field.w):
            print("X" if board[x + y * side_field.w].click else '0',end=", ")
        print("")
    print("")


def count_down_clock(*args, **kwargs):
    global remaining_time
    global start_time
    global elapse
    sec = 1
    cur_time = time.time()
    if not paused:
        elapse = cur_time - start_time
        if elapse >= sec:
                start_time = time.time()
                remaining_time -= 1
    else:
        start_time = cur_time - elapse

def set_puzzle(settings):
    makeRandomShape(settings)
    commands = turnRandom(settings)
    ## update commands:
    move_ob.moves = commands


def reset_game():
    global remaining_time
    global display
    global currentSettings
    global side_field
    global field
    global current_level
    global time_reward_fade_ob
    global result_text_fade_ob
    global swear_fade_ob
    remaining_time = PLAYTER_TIME
    display = ""
    current_level = 0
    set_settings()
    side_field.array = side_field.make_new_array()
    field.array = field.make_new_array()
    time_reward_fade_ob = FadeInEffect(still_time=1, text_colour=ORANGE)
    result_text_fade_ob = FadeInEffect(still_time=3)
    swear_fade_ob = FadeInEffect(text_colour=CYAN, still_time=2)
    if not paused:
        pause_game()

def user_reset_game(*args, **kwargs
                    ):
    if confirmBox("Resetting game", "Are you sure?"):
        reset_game()

def confirmBox(title,content):
    root = tkinter.Tk()
    root.withdraw()
    rs = mb.askokcancel(title, content)
    root.destroy()
    return rs

def record_player(root,record):
    global records
    global cleaned_records
    global difficulty
    with open(RECORDS_PATH, "wb") as data:
        records.append(record)
        pickle.dump(records, data)
    # ## also update the cleaned_records:
    # cleaned_records.append(record)
    # cleaned_records = sort_records(difficulty, cleaned_records)
    root.destroy()


def finish(lose = True):
    global current_level
    global total_elapse
    global difficulty
    def set_records():
        name = text_field.get()
        if name.strip() == "":
            return
        score = Score(name=name, difficulty=difficulty,
                      level=current_level,
                      time_spent=total_elapse, time_stamp=datetime.now())
        record_player(root,score)

    time_spent = display_ob.convert(int(total_elapse))
    root = tkinter.Tk()
    if lose:
        root.title = "Game Over!"
        label = tkinter.Label(root, text= f"You Lost!\nLevel: {current_level}\n"
                                          f"Total time spent: {time_spent}\nEnter your name here:")
    else:
        current_level = 5
        root.title = "YOU WON!!"
        label = tkinter.Label(root, text="You Won!\nTotal time spent:  " + display_ob.convert(
    int(total_elapse)) + "\nEnter your name here:")
    text_field = tkinter.Entry(root)

    # label.place(anchor='n',relheight=1, relwidth=1)
    button = tkinter.Button(root, text='ok', command = set_records)
    label.grid(row=0, columnspan=2)
    text_field.grid(row=1,column=0)
    button.grid(row=1, column=1)

    center_tk_window(root)
    root.mainloop()
    reset_game()

def center_tk_window(root, offset_x =0, offset_y = 0):
    root.update()
    w = root.winfo_width()
    h = root.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height= root.winfo_screenheight()
    x,y = (screen_width//2 - w//2 + offset_x, screen_height//2 - h//2 + offset_y)
    root.geometry("{}x{}+{}+{}".format(w,h,x,y))


def set_settings():
    global currentSettings
    global current_level
    global remaining_time
    global difficulty
    level = current_level
    if level == 0:
        currentSettings['current_shapes_num'] = DIFFICULTY_SETTINGS[difficulty].shapes_num
        currentSettings['current_moves_num'] = DIFFICULTY_SETTINGS[difficulty].moves_num
        currentSettings['current_time_reward'] = DIFFICULTY_SETTINGS[difficulty].time_reward
    elif level == 4:
        currentSettings['current_moves_num'] = DIFFICULTY_SETTINGS[difficulty].moves_num + 3
        currentSettings['current_shapes_num'] = DIFFICULTY_SETTINGS[difficulty].moves_num + 3
    elif level == 3:
        currentSettings['current_shapes_num'] = DIFFICULTY_SETTINGS[difficulty].shapes_num + 2
        currentSettings['current_moves_num'] = DIFFICULTY_SETTINGS[difficulty].moves_num + 2
    elif level == 2:
        currentSettings['current_moves_num'] = DIFFICULTY_SETTINGS[difficulty].moves_num + 1
    elif level == 1:
        currentSettings['current_shapes_num'] = DIFFICULTY_SETTINGS[difficulty].shapes_num + 1

def check_current_level(time):
    global current_level
    # if time >= 60*6:
    #     level = 5
    if time >= 60*5:
        level = 4
    elif time >= 60*4:
        level = 3
    elif time >= 60*3:
        level = 2
    elif time >= 60*2:
        level = 1
    else:
        level = 0
    
    current_level = max(current_level, level)

def sort_records(difficulty, records):
    ### sort and return top 10
    def by_time_spent(x):
        return x.time_spent
    def by_time_stamp(x):
        return x.time_stamp
    def by_level(x):
        return x.level
    records = list(filter(lambda x: x.difficulty==difficulty, records))
    records.sort(key=by_time_stamp,reverse=True)
    records.sort(key=by_time_spent)
    records.sort(key=by_level, reverse=True)

    length = len(records)
    quanity = 10
    return records[:length] if length < quanity else records[:quanity]

def display_high_scores(*args, **kwargs):
    global records
    global difficulty
    def close():
        root.destroy()
    ### clean up, sort and arrange the score records - as a list:
    cleaned_records = sort_records(difficulty, records)

    root = tkinter.Tk()
    root.title("High Scores")
    h_title = tkinter.Label(root, text=f'Top 10 High Scores for {difficulty.capitalize()} Difficulty')

    # create columns and table:
    cols = ('No.', 'Name', 'Difficult', 'Level', 'Time Spent', 'Time Stamp')
    table = ttk.Treeview(root, column=cols, show='headings')
    exit_button = tkinter.Button(root,text='Close', width=50, command=close)

    ## set columns headings:
    for i, c in enumerate(cols):
        table.heading(c, text=c, anchor=tkinter.N)
        width = 0
        if i == len(cols)-1:
            width = 200
        elif i== 1:
            width = 200
        elif i == 0:
            width = 50
        else:
            width = 100
        table.column(i, width=width)

    ## populate
    for index, score in enumerate(cleaned_records,start=1):
        time_stamp = score.time_stamp.strftime("%Y/%m/%d -- %H:%M:%S")
        time_spent = display_ob.convert(score.time_spent)
        level = score.level if score.level <= 3 else 'S' if score.level <= 4 else 'WON!'
        table.insert(parent="", index='end',
                     values=(index, score.name.upper(), score.difficulty.upper(), level
                             ,time_spent,time_stamp))
    h_title.grid(row=0, columnspan=5)
    table.grid(row=1, columnspan=1)
    exit_button.grid(row=2,columnspan=5)

    root.resizable(False, False)

    center_tk_window(root)
    root.mainloop()

def display_help(*args, **kwargs):
    def close():
        root.destroy()
    root = tkinter.Tk()
    img = ImageTk.PhotoImage(Image.open(str(image_folder / "tutorial.png")))

    label = tkinter.Label(root, image=img)
    label.pack()

    root.protocol("WM_DELETE_WINDOW", close)
    root.resizable(False, False)
    center_tk_window(root, offset_y=-300)
    root.bind("<Escape>", lambda x: close())
    root.mainloop()


def goToChooseDifficulty():
    global onChooseDifficulty
    global scr
    diff = None
    def diff_wrapper(dif):
        def choose_diff(*args, **kwargs):
            nonlocal diff
            nonlocal running
            diff = dif

            running = False

        return choose_diff


    choose_label = "PLEASE CHOOSE DIFFICULTY: "
    easy_rect_func = diff_wrapper('easy')
    easy_rect = MyRect(colour=GREEN, line_colour=WHITE, func=[easy_rect_func])
    normal_rect_func = diff_wrapper('normal')
    normal_rect = MyRect(colour=BLUE, line_colour=WHITE, func=[normal_rect_func])
    hard_rect_func = diff_wrapper('hard')
    hard_rect = MyRect(colour=BRIGHT_RED, line_colour=WHITE, func=[hard_rect_func])
    easy_button = Field(scr, x = CUBE_WIDTH*(SCREEN_WIDTH/2 - 2), y = CUBE_WIDTH*2,
                   width = 4, height= 1, rect=easy_rect, cube_width=CUBE_WIDTH, cube_height=CUBE_WIDTH, border=False,
                        line=False)
    normal_button = Field(scr, x = CUBE_WIDTH*(SCREEN_WIDTH/2 - 2), y = CUBE_WIDTH*3.5,
                        width = 4, height= 1, rect=normal_rect, cube_width=CUBE_WIDTH, cube_height=CUBE_WIDTH, border=False,
                        line=False)
    hard_button = Field(scr, x = CUBE_WIDTH*(SCREEN_WIDTH/2 - 2), y = CUBE_WIDTH*5,
                          width = 4, height= 1, rect=hard_rect, cube_width=CUBE_WIDTH, cube_height=CUBE_WIDTH, border=False,
                          line=False)
    running = True
    font = pygame.font.SysFont(my_font, size=35, bold=False)
    while running:
        # listening for clicks:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                if exit_game():
                    running = False
            if e.type == pygame.MOUSEBUTTONDOWN:
                easy_button.click(e.pos)
                normal_button.click(e.pos)
                hard_button.click(e.pos)

        display_ob.display_text(x=CUBE_WIDTH*(SCREEN_WIDTH/2),y= CUBE_WIDTH*1.5,
                                text=choose_label, centeredY=True, centeredX=True,
                                colour=WHITE)
        easy_button.draw_plain_init()
        normal_button.draw_plain_init()
        hard_button.draw_plain_init()

        display_ob.display_text(x=CUBE_WIDTH*(SCREEN_WIDTH/2),y=easy_button.posy+CUBE_WIDTH*0.5,
                                font=font,
                                text='EASY', colour=BLACK,centeredX=True,centeredY=True)
        display_ob.display_text(x=CUBE_WIDTH*(SCREEN_WIDTH/2),y=normal_button.posy+CUBE_WIDTH*0.5,
                                font=font,
                                text='NORMAL', colour=BLACK,centeredX=True,centeredY=True)
        display_ob.display_text(x=CUBE_WIDTH*(SCREEN_WIDTH/2),y=hard_button.posy+CUBE_WIDTH*0.5,
                                font=font,
                                text='HARD', colour=BLACK,centeredX=True,centeredY=True)
        pygame.display.flip()

    del easy_button, normal_button, hard_button
    onChooseDifficulty = False
    return diff


#classes:
class Field(Board):
    def draw(self):
        pass

    def update(self):
        pass

class Side(Board):
    def __init__(self, screen, x, y, width, height, cube_width, cube_height, rect):
        super().__init__(screen, x, y, width, height, cube_width, cube_height, rect, border= False)

    def update(self):
        global game_state_text
        global game_state_text_colour
        side.array[0].colour = BLACK if paused else RED

        game_state_text = "START" if paused else "PAUSE"

class MyDisplay(Display):
    RED_TIME = 30
    def my_display_clock(self, x, y, secs=0, colour = None, font=None, bg = None, centeredX = False, centeredY=False):
        if secs < self.RED_TIME:
            colour = RED
        self.display_clock(x,y,secs=secs,colour=colour,font=font,bg=bg,centeredX=centeredX,centeredY=centeredY)

class Moves():
    GAP = 15
    ## there are 4 moves: L, R, H, V
    def __init__(self, moves, img_width):
        self.moves = moves
        self.img_width = img_width

    def draw(self, x, y):
        global field
        if self.moves != None:
            width = int(abs(field.posx-x) / (self.img_width + self.GAP))
            for index,move in enumerate(self.moves):
                img = turn_commands[move]
                new_y = y
                new_x = x + index*(self.img_width+self.GAP)
                if index > width-1:
                    new_y = y + ((index // width) * (self.img_width + self.GAP))
                    index = index % width
                    new_x = x + index * (self.img_width + self.GAP)
                display_ob.display_sur(x=new_x, y=new_y, sur=img, centeredX=False, centeredY=False)


    def set_image(self, move, img_str):
        self.moves[move] = pygame.image.load(img_str).convert_alpha()

# RUN A TK LOOP BEFORE PYGAME TO AVOID CRASHING IN SOME MAC-SYSTEMS:
hidden_tk = tkinter.Tk()
# hidden_tk.protocol("WM_DELETE_WINDOW", check_tk_exit)
hidden_tk.withdraw()
hidden_tk.after(50, lambda : hidden_tk.destroy())
hidden_tk.mainloop()

# game initilization
win_posx = 500
win_posy = 100
os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (win_posx,win_posy)
pygame.mixer.pre_init()
pygame.init()
scr = pygame.display.set_mode((SCREEN_WIDTH*CUBE_WIDTH, SCREEN_HEIGHT*CUBE_WIDTH))

pygame.display.set_caption(TITLE)
scr.fill(BLACK)
pygame.display.flip()

pygame.font.init()
clock = pygame.time.Clock()

# assets -- elements -- objects:
field_rect_func = change_colour_wrapper(to_colour=SHAPE_COLOUR, from_colour=DARK_GREY)
field_rect = MyRect(border_colour=BLACK, colour=DARK_GREY, line_colour=WHITE, click_colour=SHAPE_COLOUR, func= [field_rect_func])
field = Field(scr, x=CUBE_WIDTH*MENU_W, y=CUBE_WIDTH*(SCREEN_HEIGHT-MENU_H),
              width=BOARD_W, height=BOARD_H,cube_width= CUBE_WIDTH, cube_height=CUBE_WIDTH, rect=field_rect)

side_rect = MyRect(line_colour=WHITE)
side = Side(scr, x=0, y=CUBE_WIDTH * (SCREEN_HEIGHT-MENU_H),
            width=1, height=BOARD_H, cube_width=CUBE_WIDTH * 3, cube_height=CUBE_WIDTH,rect= side_rect)


## CLICK RECTANGLE:
button_rect = MyRect(colour=CLICK_BUTTON_COLOUR, line_colour=WHITE, func=[checkBoard])
check_button = Field(scr, x = 0, y =CUBE_WIDTH * 1,
                     width = SCREEN_WIDTH, height= 1, rect=button_rect, cube_width=CUBE_WIDTH, cube_height=CUBE_WIDTH, border=False, line=None)


side_field_rect = MyRect(border_colour=BLACK, colour=DARK_GREY, line_colour=WHITE, click_colour=ORANGE, func= None)
side_field = Field(scr, x=0, y=CUBE_WIDTH*(SCREEN_HEIGHT-MENU_H+1),
              width=BOARD_W-2, height=BOARD_H-2,cube_width= CUBE_WIDTH/7, cube_height=CUBE_WIDTH/7, rect=side_field_rect, border= False)



# Menu buttons:
### pause/start button
side.array[0].colour = BLACK
pause_button_change_colour = change_colour_wrapper(to_colour=RED, from_colour=BLACK)
side.array[0].func = [pause_game]

### box displaying the puzzle
side.array[1].colour = ORANGE

### reset button
side.array[2].colour = YELLOW
side.array[2].func = [user_reset_game]

### high scores
side.array[3].colour = GREEN
side.array[3].func = [display_high_scores]

### help
side.array[4].colour = BLUE
side.array[4].func = [display_help]

### exit game
side.array[5].colour = INDIGO
side.array[5].func = [exit_game]


# in-game variables:
running = True
paused = True
font_colour = BLACK
result_board_array = []

## set up images:
root_folder = Path().parent.resolve()
image_folder = root_folder / "images"

test_img = pygame.image.load(str(image_folder / "35x35.png")).convert_alpha()
left_img = pygame.image.load(str(image_folder / "Left.png")).convert_alpha()
right_img = pygame.image.load(str(image_folder / "Right.png")).convert_alpha()
horizontal_img = pygame.image.load(str(image_folder / "Horizontal.png")).convert_alpha()
vertical_img = pygame.image.load(str(image_folder / "Vertical.png")).convert_alpha()
turn_commands = {'left':left_img, 'right':right_img, 'horizontal':horizontal_img, 'vertical':vertical_img}

### fonts and stuff:
my_font = 'ubuntu'
font = pygame.font.SysFont(my_font, size = 25, bold=True)
time_added_font = pygame.font.SysFont(my_font, size=40, bold=True)
clock_font = pygame.font.SysFont(my_font, size=60, bold=False)
clock_font_bold = pygame.font.SysFont(my_font, size=60, bold=True)
menu_font = pygame.font.SysFont("dejavusansmono", size=25, bold=False)
compare_font = pygame.font.SysFont(my_font, size=40, bold=True)
swear_font = pygame.font.SysFont(my_font, size=25, bold=True)

# non-game objects:
display_ob = MyDisplay(surface=scr, font=font, colour=font_colour)
move_ob = Moves(None, img_width=test_img.get_width())

### PROGRAM STARTS, GO TO FIRST SCREEN:
onChooseDifficulty = True
difficulty = goToChooseDifficulty()

# current stuff
current_level = 0
if difficulty is not None:
    currentSettings = { 'current_shapes_num' :DIFFICULTY_SETTINGS[difficulty].shapes_num,
                     'current_moves_num': DIFFICULTY_SETTINGS[difficulty].moves_num,
                     'current_time_reward' : DIFFICULTY_SETTINGS[difficulty].time_reward}

# import stuff from files:
records = []
if Path(RECORDS_PATH).resolve().exists():
    with open(RECORDS_PATH, "rb") as score_data:
        try:
            d = pickle.load(score_data)
            if d is not None:
                records = d
        except EOFError as e:
            print(e)

with open("text/insults_adjectives.txt", 'r') as file:
    adjs = file.readlines()

with open("text/insults_nouns.txt", 'r') as file1:
    nouns = file1.readlines()

### and cleaning them-- removing '\n':
adjs_cleaned = [insult.replace('\n', '') if ('\n' in insult) else insult for insult in adjs ]
nouns_cleaned = [insult.replace('\n', '') if ('\n' in insult) else insult for insult in nouns ]


# text variables:
display = ""
    # text on the menu:
game_state_text = "START" if paused else "PAUSE"
game_state_text_colour = WHITE

# animation effects variales:
    # fade in & out text:
time_adding = False
time_added_ani_alpha = 255
time_added_ani_start_time = 0
time_added_ani_start = True
time_added_ani_still_time = 1

time_reward_fade_ob = FadeInEffect(still_time=1, text_colour=ORANGE)
result_text_fade_ob = FadeInEffect(still_time=3)
swear_fade_ob = FadeInEffect(text_colour=CYAN, still_time=2)

remaining_time = PLAYTER_TIME
# remaining_time = 60*6 - 1

start_time = 0 # for the count down clock
total_start_time = 0 # for calculating total time
elapse = 0
total_elapse = 0
start_game = True


# GAME LOOP:
while running:
    # timing:
    clock.tick(FRAME_RATE)

    # input & update the game:
    enter_key_press = 0
    enter_key_limit = 1
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            exit_game()

        if e.type == pygame.KEYDOWN:
            if enter_key_press < enter_key_limit:
                if e.key == pygame.K_RETURN:
                    checkBoard()
                    enter_key_press = 0

            if e.key == pygame.K_p:
                pause_game()


        # mouse clicks:
        if e.type == pygame.MOUSEBUTTONDOWN:
            side.click(e.pos)
            if not paused:
                field.click(e.pos)
                check_button.click(e.pos)

        #### check current levels and adjusting things accordingly:
    if remaining_time <= 0:
        finish(lose=True)
    elif remaining_time >= 60*6:
        finish(lose=False)

        ####
    check_current_level(remaining_time)
    set_settings()

    # updating the fields
    side.update()
    count_down_clock()
    click_text = "CLICK ME TO CHECK (or ENT" \
                 "ER)!"
    click_colour = WHITE
    if not paused:
        check_button.change_colour(CLICK_BUTTON_COLOUR)
        if start_game:
            set_puzzle(currentSettings)
            start_game = False
            total_start_time = time.time()
        cur_time = time.time()
        total_elapse =  cur_time - total_start_time
        # update game elements
        field.update()
    else:
        click_colour = GREEN
        click_text = "click start to play"
        check_button.change_colour(BLACK)

        total_start_time = time.time() - total_elapse


    # draw and render:
        ## draw border and panels:
    pygame.draw.rect(scr, WHITE, pygame.Rect(0,0,SCREEN_WIDTH*CUBE_WIDTH, CUBE_WIDTH*(SCREEN_HEIGHT-BOARD_H)))

        ## draw buttons and fields:
    side.draw_plain_init()
    field.draw_plain_init()
    check_button.draw_plain_init()
    side_field.draw_plain_init()

        ## draw menu text:
    display_ob.display_text(x=CUBE_WIDTH*1.5, y=CUBE_WIDTH*2.5, text=game_state_text, centeredY=True,centeredX=True,
                            colour=game_state_text_colour, font=menu_font)
    display_ob.display_text(x=CUBE_WIDTH*1.5, y=CUBE_WIDTH*7.5, text="EXIT", centeredY=True,centeredX=True, colour=WHITE ,font=menu_font)
    display_ob.display_text(x=CUBE_WIDTH*1.5, y=CUBE_WIDTH*5.5, text="HIGH SCORES", centeredY=True,centeredX=True, colour=WHITE, font=menu_font,  )
    display_ob.display_text(x=CUBE_WIDTH*1.5, y=CUBE_WIDTH*4.5, text="RESET", centeredY=True,centeredX=True, colour=WHITE, font=menu_font)
    display_ob.display_text(x=CUBE_WIDTH*1.5, y=CUBE_WIDTH*6.5, text="HELP", centeredY=True,centeredX=True, colour=WHITE, font=menu_font)
    ### display the level label:
    level = 'level {}'.format(str(current_level if current_level < 4 else ""))
    display_ob.display_text(x=CUBE_WIDTH*0.5, y=CUBE_WIDTH*0.15, text=level, centeredY=False,centeredX=False, colour=BLACK, font=clock_font)
    if current_level == 4:
        display_ob.display_text(x=CUBE_WIDTH*1.1, y=CUBE_WIDTH*0.15, text=''.join([' ' for x in level]) + 'S',
                                centeredY=False,centeredX=False, colour=YELLOW, font=clock_font_bold)
    ### display the clock
    display_ob.my_display_clock(CUBE_WIDTH * CLOCK_POS_X, CUBE_WIDTH * CLOCK_POS_Y,
                                secs=remaining_time, centeredX=True, centeredY=True,
                                font=clock_font)
    ### display the click text:
    display_ob.display_text(x=CUBE_WIDTH * (SCREEN_WIDTH/2), y=CUBE_WIDTH * 1.5, text=click_text, centeredY=True, centeredX=True,
                            colour=click_colour)
    ### drawing the moves:
    move_ob.draw(x=side_field.w*side_field.cube_w+move_ob.GAP,y=side_field.posy)

    ## draw affects:
    if time_reward_fade_ob.on:
        reward = currentSettings['current_time_reward']
        text = "+" + str(reward)
        time_reward_fade_ob.update(font=time_added_font,fading_speed=4, text=text, colour =ORANGE)
        display_ob.display_sur(x=CUBE_WIDTH*CLOCK_POS_X, y=CUBE_WIDTH*CLOCK_POS_Y*0.3, sur=time_reward_fade_ob.text_sur, centeredX=True, centeredY=True)

    if result_text_fade_ob.on:
        colour = GREEN if display != 'WRONG!' else RED
        result_text_fade_ob.update(font=compare_font, colour = colour, fading_speed=4,text=display)
        display_ob.display_sur(x=CUBE_WIDTH*(SCREEN_WIDTH/2), y=CUBE_WIDTH*0.5, sur=result_text_fade_ob.text_sur, centeredY=True,centeredX=True)
    if swear_fade_ob.on:
        swear_fade_ob.update(font=swear_font, fading_speed=6)
        display_ob.display_sur(swear_fade_ob.x, swear_fade_ob.y, sur=swear_fade_ob.text_sur, centeredX=False, centeredY=False)
        ## executing drawing & rendering:
    pygame.display.flip()

pygame.quit()

