"""
Welcome to Spherical Cow
"""
from Board_Class import Board,set_up_board
from Bot_Class import Bot
from Tile_Class import Tile,Button,TextBox,changeSpeed,window_size,board_width,tile_spacing
from Vector_Class import V
import math,time
import pygame as pg
from pygame import gfxdraw
import pickle
from Ball_Class import Ball,Player
from random import random as rand
import random

debug = False
reset_settings = False
# This resets the settings
if reset_settings:
    pickle.dump(1, open("settings.dat", 'wb'))
# pickle.dump(0,open('High_Score.dat','wb'))


def data_dump(): #This exports settings info to an external file
    pickle.dump(1, open("settings.dat", 'wb'))
    if debug: #This information has hopefully been saved in the data file
        assert 1==pickle.load(open("settings.dat", 'rb'))
    pass


# COLORS!
othello_color = (220,220,220)
light_button_color = (150, 150, 150)            # These are used for buttons in the settings page
background_color=(34,34,34)
play_text_color=(30,30,30)
board_color = (115,49,82)# V((49,115,82))# (61,143,102)
dark_button_color=board_color
setting_label_color=(190,190,190)
bubble_color=(90,90,90)             # Color of sliders

# Below are the settings in order, as imported from the data file.
# Animation speed, difficulty (white player) level, True or False playing 0-player
# black player level, undo enabled, skip enabled, show legal moves enabled?
speed_l, diff_l, single_bot, double_bot, p2_l, undo_on, skip_on, show_moves_on = pickle.load(open("settings.dat", 'rb'))

#Get the game started
# This places the top left corner of the board ->
window_offset=V(((window_size[0]-board_width)/2,(window_size[1]-board_width)/2+50))
screen=pg.display.set_mode(window_size) # This makes the display
pg.init()
########################################################################################################################
#                                       IMAGES AND SHAPES
########################################################################################################################
if True:
    # board_images=[pg.Surface((board_width,board_width)) for i in range(5)]
    # for i,im in enumerate(board_images):
    #     n=2*i+4
    #     im.fill(board_color)
    #     for l in range(n+1):
    #         pg.draw.line(im,(0,0,0),(l*(board_width-2)/n,0),(l*(board_width-2)/n,board_width),width=2)
    #         pg.draw.line(im, (0, 0, 0), (0,l * (board_width-2) / n), (board_width,l * (board_width-2) / n), width=2)
    # board_image_rects=[image.get_rect() for image in board_images]
    # for tangle in board_image_rects:
    #     tangle.center=window_offset+V((board_width,board_width))/2

    # board_image_shrunks=[pg.Surface((board_width/2,board_width/2)) for i in range(5)]
    # for i,im in enumerate(board_image_shrunks):
    #     n=2*i+4
    #     im.fill(board_color)
    #     for l in range(n+1):
    #         pg.draw.line(im,(0,0,0),(l*(board_width-1)/n/2,0),(l*(board_width-1)/n/2,board_width),width=1)
    #         pg.draw.line(im,(0,0,0),(0,l*(board_width-1)/n/2),(board_width/2,l*(board_width-1)/n/2),width=1)
    #
    # board_image_shrunk_rects = [shrunk.get_rect() for shrunk in board_image_shrunks]  # Rectangle for title screen
    # for tangle in board_image_shrunk_rects:
    #     tangle.midtop = (window_size[0] / 2, 100)  # Place them near the middle of the window

    background=pg.Surface(window_size) #background surface
    background.fill((148,172,136))
    background.fill(background_color)
    changeSpeed(1.4 ** (speed_l - 5))   # Changes animation speed based on speed level
    line_length = 300                   # Length of settings slider line
    diff_h = 30                         # Height of difficulty slider
    p2_h=130                            # Height of white player slider
    speed_h = -120                      # Height of speed slider
    # Set players below, whether double bot, single bot, or no bot
    # if double_bot:
    #     players=[bots[p2_l],bots[diff_l]]   # players=["human",bots[diff_l]]
    # elif single_bot:
    #     players = ['human', bots[diff_l]]
    # else:
    #     players = ['human',"human"]
########################################################################################################################
#                                       BUTTONS AND TEXT
########################################################################################################################
if True:
    # Make pygame fonts
    othello_font=pg.font.SysFont('Helvetica',60,bold=False)
    game_over_font=pg.font.SysFont('Helvetica',60,bold=True)
    turn_font=pg.font.SysFont('calibri',30,bold=False)
    skip_font=pg.font.SysFont('calibri',35,bold=False)
    board_size_font = pg.font.SysFont('calibri', 30, bold=True)
    scale_font = pg.font.SysFont('calibri', 20)
    show_moves_font = pg.font.SysFont('calibri', 18)
    settings_label_font=pg.font.SysFont('calibri', 30)
    settings_button_font=pg.font.SysFont('calibri',33,bold=False)
    play_font = pg.font.SysFont('calibri',40,bold=False)
    # settings_button_font #pg.font.SysFont('Helvetica', 50, bold=False)


    #Making buttons!
    skip_button=Button((window_offset[0]-50,50),dark_button_color,"Skip",(20,20,20),skip_font)
    skip_button.midleft((10, window_size[1] / 2))
    undo_button=Button((window_offset[0]-50,50),dark_button_color,"Undo",(20,20,20),skip_font)
    undo_button.midleft((10, window_size[1] / 2-70))
    quit_button=Button((window_offset[0]-50,50),dark_button_color,'Quit',(20,20,20),skip_font)
    quit_button.midleft((10,window_size[1]/2+70))

    play_button=Button((250,70),dark_button_color,"Play Game",play_text_color,play_font)
    play_button.center((window_size/2+V((0,110))))
    settings_button=Button((210,60),light_button_color,"Settings",(20,20,20),settings_button_font)
    settings_button.center((window_size/2+V((0,210))))

    # size_strings=["{} x {}".format(i*2+4,i*2+4) for i in range(len(board_images))]
    # board_size_buttons = [Button((100, 42),light_button_color,i,(40,40,40),board_size_font,thickness=1) for i in size_strings]
    # for i, button in enumerate(board_size_buttons):
    #     button.center((window_size[0] / 2 + 250, 110 + i * 65)) #Place them on the board

    #These buttons are for the different play options
    bot_buttons_h=-55
    double_bot_button=Button((80,40),light_button_color,"0 Player",(10,10,10),scale_font,thickness=1)
    double_bot_button.center(window_size/2+V((-line_length/2,bot_buttons_h)))
    no_bot_button=Button((80,40),light_button_color,"2 Player",(10,10,10),scale_font,thickness=1)
    no_bot_button.center(window_size/2+V((line_length/2,bot_buttons_h)))
    single_bot_button=Button((80,40),light_button_color,"1 Player",(10,10,10),scale_font,thickness=1)
    single_bot_button.center(window_size/2+V((0,bot_buttons_h)))
    # Changing color to reflect which play option is selected.
    if single_bot:
        single_bot_button.changeColor(dark_button_color)
    elif double_bot:
        double_bot_button.changeColor(dark_button_color)
    else:
        no_bot_button.changeColor(dark_button_color)

    #Undo, Skip, and Show moves enabled buttons!
    undo_setting_button = Button((90, 40), light_button_color, "Undo: OFF", (10, 10, 10), scale_font, thickness=1)
    undo_setting_button.center(window_size/2+V((-100,-200)))
    if undo_on:
        undo_setting_button.changeColor(dark_button_color)
        undo_setting_button.changeText("Undo: ON")
    skip_setting_button = Button((90, 40), light_button_color, "Skip: OFF", (10, 10, 10), scale_font, thickness=1)
    skip_setting_button.center(window_size/2+V((0,-200)))
    if skip_on:
        skip_setting_button.changeColor(dark_button_color)
        skip_setting_button.changeText("Skip: ON")
    show_moves_button = Button((130, 40), light_button_color, "Show Moves: OFF", (10, 10, 10), show_moves_font, thickness=1)
    show_moves_button.center(window_size/2+V((120,-200)))
    if show_moves_on:
        show_moves_button.changeColor(dark_button_color)
        show_moves_button.changeText("Show Moves: ON")

    # The sliders are just buttons with text shifted down
    slider_size=(12,30)
    slider_shift=V((0,27)) # This shifts the text down underneath the slider 25 pixels
    diff_slider=Button(slider_size,bubble_color,str(diff_l),othello_color,scale_font,thickness=1)
    diff_slider.center((window_size/2+((diff_l-5)*line_length/10,diff_h)))
    diff_slider.shiftText(slider_shift)
    p2_slider=Button(slider_size,bubble_color,str(p2_l),othello_color,scale_font,thickness=1)
    p2_slider.center((window_size/2+((p2_l-5)*line_length/10,p2_h)))
    p2_slider.shiftText(slider_shift)
    speed_slider=Button(slider_size,bubble_color,str(round(1.4 ** (speed_l - 5),1)),othello_color,scale_font,thickness=1)
    speed_slider.center((window_size/2+((speed_l-5)*line_length/10,speed_h)))
    speed_slider.shiftText(slider_shift)
    if speed_l>10: speed_slider.changeText("MAX") #In case the maximum speed is chosen

    # These are just plain text which we'll put on the screen
    # In game text:
    othello_box=TextBox("OTHELLO",othello_color,othello_font)
    othello_box.center((window_size[0]/2,40))
    turn_box=TextBox("Black Turn",(0,0,0),turn_font)
    turn_box.center((window_size[0]/2,95))
    white_score_box=TextBox("2",(255,255,255),turn_font)
    white_score_box.center(((board_width+3*window_size[0])/4,350))
    black_score_box=TextBox("2",(0,0,0),turn_font)
    black_score_box.center(((board_width+3*window_size[0])/4,300))
    scores_box=TextBox("Scores:",othello_color,turn_font)
    scores_box.center(((board_width+3*window_size[0])/4,250))
    game_over_button=Button((300,80),background_color+V((10,10,10)),"Game Over",(255,255,255),game_over_font,thickness=3)
    game_over_button.center(window_size/2)
    #Text in Settings
    diff_label_box=TextBox("Difficulty",setting_label_color,settings_label_font)
    diff_label_box.center((window_size/2+V((0,diff_h-35))))
    p1_label_box=TextBox("White Bot",setting_label_color,settings_label_font)
    p1_label_box.center((window_size / 2 + V((0, diff_h - 35))))
    p2_label_box=TextBox("Black Bot",setting_label_color,settings_label_font)
    p2_label_box.center((window_size/2+V((0,p2_h-35))))
    speed_label_box=TextBox("Speed",setting_label_color,settings_label_font)
    speed_label_box.center((window_size/2+V((0,speed_h-35))))
########################################################################################################################


newball=Ball((100,100),(1,0),1,20,(100,0,0))
twoball=Ball((150,100),(0,1),4,40,color=(0,100,0))
balls=[]
# balls.append(newball); balls.append(twoball)

for i in range(20):
    print(rand())
def randfrom(a,b):
    return a+rand()*(b-a)

def generateBalls():
    balls=[]
    avsize = 30
    tamass = 1
    taen = 1
    nballs = 7
    var = .5
    for i in range(nballs):
        mvar=tamass*(-var+var*2*rand())
        mass=tamass+mvar
        envar=taen*(-var+var*2*rand())
        en=taen+envar
        if i<nballs-1:
            tamass-=mvar/(nballs-i-1)
            taen-=envar/(nballs-i-1)
        vel=((en/mass)**(1/2),0)
        # pos=(random()*500+200,random()*500+200)
        pos=(10*i,10*i)
        balls.append(Ball(pos,vel,mass,avsize*mass**(1/2),(0,i*20,0)))
    return balls

def genBalls(num,siz,en,variance=0.5):
    balls=[]
    Min=1-variance
    Max=1+variance
    totmass=0
    toten=0
    for i in range(num):
        rem=num-i-1
        imin=max(Min,num-Max*rem-totmass)
        imax=min(Max,num-Min*rem-totmass)
        mass= imin+rand()*(imax-imin)
        totmass+=mass
        imin=max(Min,num-Max*rem-toten)
        imax=min(Max,num-Min*rem-toten)
        energy= imin+rand()*(imax-imin)
        toten+=energy
        size=siz*mass**(1/2)
        pos=(size+rand()*(window_size[0]-2*size),size+rand()*(window_size[1]-2*size))
        vel=V(((en*energy/mass)**(1/2),0))
        vel=vel.rotated(rand()*6.28)
        cval=200/num*i
        balls.append(Ball(pos,vel,mass,size,(200-cval,cval,0)))
    print("mass is {}".format(sum([i.mass for i in balls])))
    print("energy is {}".format(sum([i.kinetic_energy() for i in balls])))
    return balls

def is_game_over(balls,player):
    for ball in balls:
        if ball.check_ball_collision(player):
            return True
    return False
candy_image=pg.image.load("images/Candy.gif").convert_alpha()
def add_candy(player):
    newpos = (5 + rand() * (window_size[0] - 10), 5 + rand() * (window_size[1] - 10))
    while player.pos.dist(newpos)<abs(window_size)/4:
        newpos = (5 + rand() * (window_size[0] - 10), 5 + rand() * (window_size[1] - 10))
    candy.append(Ball(newpos,(0,0),1,5,(250,250,0),image=candy_image))


highscore=pickle.load(open('High_Score.dat','rb'))


energy_monitor=TextBox("Kinetic Energy: {}".format(0),(250,250,250))
energy_monitor.center((600,100))
score_monitor=TextBox("Score: {}".format(0),(250,250,250))
score_monitor.center((600,130))
candies_monitor=TextBox("Score: {}".format(0),(250,250,250))
candies_monitor.center((600,160))
highscore_monitor=TextBox("High Score: {}".format(0),(250,250,250))
highscore_monitor.center((600,190))

# Initialize Stuff
# set_board_size(8)       # Set board up
clock=pg.time.Clock()   # pygame thing
game_active = False     # Start in the title screen
settings_open = False
left_clicking=None      # Not clicking on anything
game_over=True
blocked=True
counter=0               # Reset
player=Player(pg.mouse.get_pos(),(0,0),1,10,(0,0,100))
player_speed=5
game_speed=2
candy=[]
energy_increment=0.01
score=0
candies=0
########################################################################################################################
#                                           MAIN LOOP
########################################################################################################################
while True:
    for event in pg.event.get():
        if event.type==pg.QUIT:
            pg.quit()
            exit()
        #####################################################################################
        if game_active:                 # GAME ACTIVE
            if event.type == pg.MOUSEBUTTONDOWN:
                if quit_button.collidepoint(event.pos) and event.button==1:
                    left_clicking = "quit" #quit button selected (always allowed, even when animations active)
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            elif event.type == pg.MOUSEBUTTONUP: #On upclick
                if event.button==1:
                    if left_clicking=="quit" and quit_button.collidepoint(event.pos):
                        game_active=False

                    left_clicking = None

        #####################################################################################
        elif settings_open:             # SETTINGS PAGE
            if event.type==pg.MOUSEBUTTONDOWN:
                if event.button==1: #Leftclick down
                    loc=event.pos
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            elif event.type==pg.MOUSEBUTTONUP:
                if event.button==1: #Leftclick up
                    left_clicking=None
        #####################################################################################
        else:                           # TITLE PAGE
            if event.type==pg.MOUSEBUTTONDOWN:
                if event.button==1: #Leftclick down
                    if play_button.collidepoint(event.pos):
                        left_clicking = 'play'          # Play button selected
                    elif settings_button.collidepoint(event.pos):
                        left_clicking = 'open_settings' # Settings button selected
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            elif event.type==pg.MOUSEBUTTONUP:
                if event.button==1: #Leftclick up
                    if left_clicking=='play' and play_button.collidepoint(event.pos):
                        player.goto(pg.mouse.get_pos())
                        highscore = max(score, highscore)
                        temp_speed=0
                        score=0
                        candies=0
                        highscore_monitor.changeText("High Score: {}".format(highscore))
                        pickle.dump(highscore,open("High_Score.dat","wb"))
                        while game_over:
                            balls = genBalls(20, 30, 1, .3)
                            game_over = is_game_over(balls,player)
                        game_active=True
                        add_candy(player)
                        add_candy(player)
                        # game_over=False
                    left_clicking=None #upclick means nothing's clicked
    ###########################################################################################################
    ###########################################################################################################
    # No matter what, we always have the background and OTHELLO
    screen.blit(background, (0, 0))
    energy_monitor.blit(screen)
    score_monitor.blit(screen)
    candies_monitor.blit(screen)
    highscore_monitor.blit(screen)
    total_energy=sum([i.kinetic_energy() for i in balls])
    energy_monitor.changeText("Kinetic Energy: {}".format(round(total_energy,2)))
    score_monitor.changeText("Score: {}".format(score))
    candies_monitor.changeText("Candies: {}".format(candies))
    # othello_box.blit(screen)
    if game_active:
        quit_button.blit(screen,left_clicking=='quit') #Quit button, highlighted if selected
        if not game_over:
            score+=int(total_energy)
            # print("total energy is ",sum([i.kinetic_energy() for i in balls]))
            for i, ball in enumerate(balls):
                ball.walls(0, 0, *(window_size), 1)
                # ball.accelerate((0,.2))
                for b in balls[i + 1:]:
                    if ball.check_ball_collision(b):
                        ball.ball_collision(b, 1)
            game_over = is_game_over(balls, player)
            # player.goto(pg.mouse.get_pos())
            player.vel = (pg.mouse.get_pos() - player.pos).normalize() * min(player_speed,player.pos.dist(pg.mouse.get_pos())/game_speed)
            if temp_speed==game_speed:
                for ball in balls:
                    ball.move(game_speed)
                player.move(game_speed)
            else:
                for ball in balls:
                    ball.move(temp_speed)
                player.move(temp_speed)
                # print(temp_speed)
                temp_speed+=.4       #Speed buildup rate
                if temp_speed>=game_speed:
                    temp_speed=game_speed
            balls=sorted(balls,key=lambda y: y.kinetic_energy())
            e=balls[-1].kinetic_energy()
            balls[-1].vel=balls[-1].vel*((e+energy_increment)/e)**(1/2)
            if game_over:
                candy = []
        for c in candy:
            if c.check_ball_collision(player):
                score+=5000
                candies+=1
                candy.remove(c)
                add_candy(player)
        for ball in balls:
            ball.blit(screen)
        for c in candy:
            c.blit(screen)
        player.blit(screen)
        if game_over:
            energy_monitor.blit(screen)
            score_monitor.blit(screen)
    else:
        settings_button.blit(screen,left_clicking in ('open_settings','close_settings'))
        ######################################################################################################
        if settings_open:
            pass
            # if left_clicking=='speed':
            #     x_pos = pg.mouse.get_pos()[0]  # use mouse position to set speed
            #     speed_l=max(round((x_pos-window_size[0]/2)*10/line_length+5),0)
            #     if speed_l>10 and speed_l<11:  # Speed lvl 12 is the secret max lvl
            #         speed_l=10
            #     if speed_l>=11:
            #         speed_l=11
            #         changeSpeed(100000)                 # Max speed
            #         speed_slider.changeText("MAX")
            #         new_center = window_size[0]/2+line_length*0.6
            #     else:
            #         changingspeed = 1.4 ** (speed_l-5)  # Set speed and text
            #         speed_slider.changeText(str(round(changingspeed,1)))
            #         changeSpeed(changingspeed)          # Change tile animations
            #         new_center = min(max(x_pos,window_size[0]/2-line_length/2),window_size[0]/2+line_length/2)
            #     speed_slider.centerx(new_center)        # Move slider
            # speed_slider.blit(screen,left_clicking=="speed") # Draw slider
        else:   # TITLE SCREEN
            play_button.blit(screen,left_clicking=='play')          # Play button

    # newball.blit(screen)
    # twoball.blit(screen)
    # newball.move(gamespeed)
    # newball.walls(0,0,*(window_size/3))
    # twoball.move(gamespeed)
    # twoball.walls(0,0,*(window_size/3))
    # if newball.check_ball_collision(twoball):
    #     print('colliding')
    #     newball.ball_collision(twoball,1)
    pg.display.update()
    clock.tick(60) # Limits to 60 fps