"""
This game is Othello, also known as Reversi. The object
of this game is to make sandwiches of your opponents tiles,
flipping them over to your color (which will be black).
These sandwiches can be any thickness, so long as they
are bookended by one existing black tile and one new
black tile.

RUNNING THE CODE:
 - Run Main to play.
 - At line 45 of this file:
    () Debug activates the pre/post-conditions
    () reset_settings resets the game settings in the in-game "Settings" screen

FEATURES:
 - Look in settings to change anything you want. These changes are saved permanently in a separate file,
   so if you close the game and reopen, it will be saved.
   () Speed is for the animations.
        [] Animations include placing, flipping, and removing
        [] Off the right side of the speed slider, you can get "MAX" speed
   () Show Moves will show you all of the possible moves you can make on the board
 - Board sizes from 4x4 to 12x12 are available:
    () 8x8 is recommended (and standard)
    () Bots are slower on larger boards (more possible moves to think about)
 - Bots: Test as much as you like, but each bot typically beats the one below.
    () The lvl 0 bot is different. It chooses a move randomly and won't skip unless forced to.
    () The lvl 10 bot will be a bit slow, but lvl 8 is more skilled than me and will beat you.
 - Undo and Skip can be deactivated (in real life they don't exist)
    () If skip is off, the Bots will avoid skipping unless necessary.
        [] If skip is on, Bots will skip if it's strategic, but only a few times in a row before
            getting bored and making a move.
    () If skip is off, it turns back on temporarily if you have no available moves.
    () After "game over", Undo button resets the board.
 - Scorekeepers show current scores
 - Progress bar with animation show current scores and game progress
 - Quit button is always active unless a Bot is thinking.

"""
from Board_Class import Board,set_up_board
from Bot_Class import Bot
from Tile_Class import Tile,Button,TextBox,changeSpeed,window_size,board_width,tile_spacing
from Vector_Class import V
import math,time
import pygame as pg
from pygame import gfxdraw
import pickle

debug = False
reset_settings = False
# This resets the settings
if reset_settings:
    pickle.dump((4, 8,True,False,3,True,True,True), open("settings.dat", 'wb'))

def flipTiles(flips): #Given flips, a generator of tuples, we flip those coords
    global scores
    if debug: #Precondition: all the flips point to actual tiles
        for x,y in flips:
            assert isinstance(tile_list[y][x],Tile)
    for x,y in flips:
        tile_list[y][x].flip()                 #This turns over the tile
    pass
def roboTurn(bot):
    if debug: #Preconditions: Game isn't over, player is a Bot
        assert isinstance(players[turn],Bot)
        assert B.emptySpaces()>0
        assert game_over==False
    # We go back to the spot in our memory, either as far back as we can,
    # or to the patience limit of the bot.
    memoryspot=(-1)*min(bot.patience,len(memory))
    #If the board hasn't changed in that long, we should disqualify skipping as an option
    # Allow skips only if the memoryspot is not the same as the board and skips are allowed.
    AllowSkips=memory[memoryspot]!=B and memory[memoryspot].inverted()!=B and skip_on
    # The bot will choose a move and only skip if they HAVE to or they're allowed to.
    bestMove=bot.chooseMove(B,AllowSkips) #This returns a tuple of board position
    if bestMove[0]==-5: # -5 is a kind of code word meaning to skip
        print("Bot passes")
    else:
        #the best move is a tuple, so we use * to unpack the coords and move to there
        moveTo(*bestMove)
    nextTurn()
    if debug: #Postcondition, the move should be legal, if it's not a pass
        if bestMove!=(-5,-5):
            B.isLegal(*bestMove)
def moveTo(xspot,yspot): # This adds a tile to a location given that it is legal
    global turn, B
    if debug: # Precondition: this move should be legal
        assert B.isLegal(xspot,yspot)
    #Put the turtle down in the right spot in the right color
    tile_list[yspot][xspot]=(Tile(xspot, yspot, turn,sw))
    B, flips = B.placeTile(xspot, yspot)  #Place tile and get the new board and flips
    flipTiles(flips) #Flip the tiles
    updateScores()
    if debug: #Postcondition: Flipping no tiles is illegal
        assert len(flips)>0
def nextTurn():
    global turn,no_moves,B
    # The board is always from the players perspective.
    # Different player? Flip the perspective.
    updateScores()
    if turn==1:
        turn=0
        memory.append(B.inverted())
    else:
        turn=1
        memory.append(B)
    #Next, we add the board to memory. The memory is strictly from Black's perspective.
    #As a result, if it's White's turn (turn==1), we remember the inverted board
    B = B.inverted()
    #Check if the game's over by tile count. If nobody can move, the game ends.
    if B.emptySpaces() == 0 or ((not B.areLegalMoves()) and (not (B.inverted()).areLegalMoves())):
        gameOver()
    else:
        # This allows players to skip even if skip is disabled.
        no_moves = not B.areLegalMoves()
        update_turn_text()
    if debug: #Postconditions: the sum of tiles should add to the sum of scores
        assert B.countTiles()==sum(scores)
def undo():
    global turn,B,game_over,no_moves
    if debug: #Preconditions: we must have some memory to look through, and at least 4 tiles on the board
        assert len(memory)>0
        assert sum(scores)>=4
    print(game_over)
    if game_over: #At the end of the game, undo means start over.
        while len(memory)>1:
            memory.pop() #This backs up the memory to the beginning
        global black_prog,white_prog
        black_prog=0; white_prog=0      # Reset the progress bar.
        turn=0                          # Reset turn
        B = set_up_board(boardSize)     # Reset board
        game_over=False                 # Reset game_over
    else:
        def backup():
            global turn, B
            memory.pop()                # Back up 1
            B =memory[-1]               # Revert to last memory
            turn=(turn+1)%2             # Switch turn
            if turn==1:                 # Memories are stored from Black's perspective, so we must invert for White
                # B.invert()
                B=B.inverted()
        backup()                        # Backup once, and then again if there's a bot on the other side
        if players[turn] != "human": backup()
    updateScores()
    updateTileList(B)                       # Flip and remove necessary tiles
    update_turn_text()
    no_moves = not B.areLegalMoves()        # Allows players to skip even if skip is disabled.
    if debug: #Postcondition: If the game was over, we restarted. We can't have less than 2 open spaces
        assert B.emptySpaces()>1
def gameOver():
    global game_over
    if debug: # Precondition: Nobody is able to play anymore.
        assert not (B.areLegalMoves() or B.inverted().areLegalMoves())
    game_over=True # Makes sense lol
    update_turn_text()
def getBots():
    # This just makes a list of bots to choose from later. Parameters defined in Bot_Class
    BabyBot= Bot(1, 1, depth=0, name="BabyBot")
    SillyBot  = Bot(4, 16, depth=0, name="SillyBot")
    ThinkerBot = Bot(100, 10000, depth=0, name="ThinkerBot")
    CleverBot = Bot(100, 10000, depth=.5, name="CleverBot")
    Megamind = Bot(100, 10000, depth=1, name="Megamind")
    Sherlock = Bot(100, 10000, depth=1.5, name="Sherlock")
    Data  = Bot(100, 10000, depth=2, name="Data")
    VIKI = Bot(100, 10000, depth=2.5, name="VIKI")
    Ultron = Bot(100, 10000, depth=3, name="Ultron")
    HAL = Bot(100, 10000, depth=4, name="HAL")
    Skynet = Bot(100, 10000, depth=5, name="Skynet")
    Rando=Bot(100, 10000, depth=0,name="Rando",RANDOM=True)
    # List of bots:
    bots=[Rando,BabyBot,SillyBot,ThinkerBot,CleverBot,Megamind,Sherlock,Data,VIKI,Ultron,HAL]

    if debug: #Postcondition: list of 11 bots
        for i in bots:
            assert isinstance(i,Bot)
        assert len(bots)==11
    return bots
def updateTileList(board):
    global tiles_to_remove
    if debug: # We are matching the tile list to the board, must be the same size
        assert len(board)==len(tile_list)
        assert len(board[0])==len(tile_list[0])
    # We search through the entire tileList
    for r, row in enumerate(tile_list):
        for e, element in enumerate(tile_list):
            bval=board[r][e]*(turn*2-1)
            tval=tile_list[r][e]
            if bval==0: #If theres no game piece here, destroy the pieces
                if tval!= None: #If there is a piece
                    tiles_to_remove.append(tval)    # List for animations
                    tile_list[r][e]=None            # Take it off the list for gameplay
                    tval.remove()                   # Tile function
            else: # This means there should be a tile
                if tval!=None: #If theres's a tile here, check if it agrees:
                    if tval.color_index!=(bval+1)/2:
                        tval.flip() # If it doesn't agree with the board, flip it
                if tval==None:
                    tile_list[r][e]=Tile(e,r,int((bval+1)/2),sw) # Place a new tile; there should be one but there isn't
    if debug: #Postcondition: Same number of tiles as there are on the board
        assert board.countTiles()==sum([isinstance(tile,Tile) for row in tile_list for tile in row])
    pass
def set_board_size(input): #This function sets up the board and a LOT of variables
    global board_image,board_image_rect, game_over
    global board_image_shrunk_rect, board_image_shrunk
    global boardSize, B, tile_list, sw, memory, turn
    global tiles_to_remove,black_prog,white_prog
    game_over=False     # Reset this for sure
    tiles_to_remove=[]  # For removal animations
    black_prog=0        # Set or Reset progress bar
    white_prog=0        # Progress bar
    i=int((input-4)/2)  # This is the index of the board size. For 4x4, it's 0, for 6x6, it's 1, etc.
    turn=0              # Set or Reset turn
    board_image=board_images[i] # Get board image surface
    board_image_rect=board_image_rects[i]
    board_image_shrunk=board_image_shrunks[i] # Get shrunk board image for title screen
    board_image_shrunk_rect=board_image_shrunk_rects[i]
    for button in board_size_buttons: # Change button color to reflect selection
        button.changeColor(board_size_button_color)
    board_size_buttons[i].changeColor(dark_board_size_button_color)
    boardSize=input                 # Set or Update this variable
    sw = board_width / boardSize    # Set or Update (Square Width)
    B = set_up_board(boardSize)     # The Board!
    tile_list = [[None for i in row] for row in B]  # Brand new tile list in the proper size
    memory = [B]                                    # Set or Reset memory
    updateTileList(B)                               # Places the first tiles
    update_turn_text()
def updateScores(): #This updates the progress bar and changes the score display surfaces
    if debug: # Precondition: The board must be made of numbers in [0,-1,1]
        for row in B:
            for i in row:
                assert i==0 or i==1 or i==-1

    blackAdv=(1-turn*2)*sum([sum(i) for i in B])       # B - W
    tileCount=B.countTiles()                # B + W
    scores[0]=int((blackAdv+tileCount)/2)   # B
    scores[1]=int((tileCount-blackAdv)/2)   # W

    # Render and place the scores:
    white_score_box.changeText(str(scores[1]))
    black_score_box.changeText(str(scores[0]))
    # Also update the progress bar. Reactivate the animation.
    global animating_prog_bar
    animating_prog_bar=True

    if debug:
        assert sum(scores)==B.countTiles()
        assert sum([sum(i) for i in B])==(1-2*turn)*(scores[0]-scores[1])
    pass
def animate_prog_bar():
    global black_prog, white_prog,animating_prog_bar
    if debug:
        assert 0<=scores[0]<=len(B)*len(B)
        assert 0<=scores[1]<=len(B)*len(B)
    m=9                 # Resolution of progress bar
    d=1+2*double_bot    # Step size. Two bots play so fast, we have to speed it up.
    # These move the progress up or down appropriately
    if   scores[0]*m>black_prog: black_prog+=d
    elif scores[0]*m<black_prog: black_prog-=d
    if   scores[1]*m>white_prog: white_prog+=d
    elif scores[1]*m<white_prog: white_prog-=d
    # If they're exactly at the right position, stop the animation.
    if scores[0]*m==black_prog and scores[1]*m==white_prog: animating_prog_bar=False
    #Draw the bar:
    prog_bar.fill(dark_button_color)                    # Background
    black_perc=black_prog/len(B)/len(B)/m           # Black Percentage
    tangle=pg.Rect((0,0),(prog_bar_size[0],black_perc*prog_bar_size[1]))
    pg.draw.rect(prog_bar,(20, 20, 20),tangle,border_radius=2)      # Black bar
    white_perc=white_prog/len(B)/len(B)/m           # White Percentage
    tangle = pg.Rect((0, (1-white_perc) * prog_bar_size[1]), (prog_bar_size[0], prog_bar_size[1]))
    pg.draw.rect(prog_bar,(200, 200, 200),tangle,border_radius=2)   # White bar
    # Draw a line at the midpoint.
    y_cord=prog_bar_size[1]/2
    if black_perc>.5:
        pg.draw.line(prog_bar, (220, 220, 220), (0, y_cord),(prog_bar_size[0],y_cord),1)
    else:
        pg.draw.line(prog_bar, (0, 0, 0), (0, y_cord), (prog_bar_size[0], y_cord), 1)
    if debug:
        assert 0 <= black_perc <= 1
        assert 0 <= white_perc <= 1
    pass
def data_dump(): #This exports settings info to an external file
    pickle.dump((speed_l, diff_l, single_bot, double_bot, p2_l, undo_on, skip_on,show_moves_on), open("settings.dat", 'wb'))
    if debug: #This information has hopefully been saved in the data file
        assert (speed_l,diff_l,single_bot,double_bot,p2_l,undo_on,skip_on,show_moves_on)==pickle.load(open("settings.dat", 'rb'))
    pass
def update_turn_text():
    if game_over: # If it's game over, check who won
        if scores[1] > scores[0]:
            turn_box.changeText("White Wins!", (210, 210, 210))
        elif scores[1] < scores[0]:
            turn_box.changeText("Black Wins!", (0, 0, 0))
        else:
            turn_box.changeText("Tie Game!", board_color)
    else:
        if turn==1: # If it's not game over, see whose turn it is
            turn_box.changeText("White Turn",(210,210,210))
        else:
            turn_box.changeText("Black Turn",(0,0,0))

othello_color = (220,220,220)
light_button_color = (150, 150, 150)            # These are used for buttons in the settings page
dark_button_color = (49,115,82)# (85, 130, 75)
board_size_button_color = light_button_color#(117, 129, 107)       # These two colors indicate what board size is selected.
dark_board_size_button_color = dark_button_color #(85, 110, 86)
play_button_color=dark_button_color# (0,100,0)
quit_button_color=dark_button_color# (0,100,0)
skip_button_color=dark_button_color# (100,100,100)
undo_button_color= dark_button_color# (150,100,100)
# background_color=(34,34,34)
background_color=(44,44,44)
play_text_color=(30,30,30)

board_color = V(dark_button_color)# (61,143,102)
# othello_color=(20,20,20)

setting_label_color=(190,190,190)
bubble_color=(90,90,90)             # Color of sliders
slider_text_color = othello_color

#Get the game started
bots=getBots() #List of bots
# This places the top left corner of the board ->
window_offset=V(((window_size[0]-board_width)/2,(window_size[1]-board_width)/2+50))
screen=pg.display.set_mode(window_size) # This makes the display
pg.init()
########################################################################################################################
#                                       IMAGES AND SHAPES
########################################################################################################################
if True:
    # This uploads the files from inside the folder
    # d_str=['Board_Images\\'+str(i*2+4)+'by'+str(i*2+4)+'Board512.png' for i in range(5)]
    # board_images=[pg.image.load(d).convert() for d in d_str]
    # board_image_rects=[image.get_rect() for image in board_images] #Get pg rectangles
    # for tangle in board_image_rects:
    #     tangle.center=window_offset+V((board_width,board_width))/2 # Place them in the middle of the window
    # board_image_shrunks=[pg.transform.rotozoom(image,0,0.5) for image in board_images] #small image for title screen
    # board_image_shrunk_rects=[shrunk.get_rect() for shrunk in board_image_shrunks] # Rectangle for title screen
    # for tangle in board_image_shrunk_rects:
    #     tangle.midtop=(window_size[0]/2,90) #Place them near the middle of the window
    board_images=[pg.Surface((board_width,board_width)) for i in range(5)]
    for i,im in enumerate(board_images):
        n=2*i+4
        im.fill(board_color)
        for l in range(n+1):
            pg.draw.line(im,(0,0,0),(l*(board_width-2)/n,0),(l*(board_width-2)/n,board_width),width=2)
            pg.draw.line(im, (0, 0, 0), (0,l * (board_width-2) / n), (board_width,l * (board_width-2) / n), width=2)
    board_image_rects=[image.get_rect() for image in board_images]
    for tangle in board_image_rects:
        tangle.center=window_offset+V((board_width,board_width))/2

    board_image_shrunks=[pg.Surface((board_width/2,board_width/2)) for i in range(5)]
    for i,im in enumerate(board_image_shrunks):
        n=2*i+4
        im.fill(board_color)
        for l in range(n+1):
            pg.draw.line(im,(0,0,0),(l*(board_width-1)/n/2,0),(l*(board_width-1)/n/2,board_width),width=1)
            pg.draw.line(im,(0,0,0),(0,l*(board_width-1)/n/2),(board_width/2,l*(board_width-1)/n/2),width=1)

    board_image_shrunk_rects = [shrunk.get_rect() for shrunk in board_image_shrunks]  # Rectangle for title screen
    for tangle in board_image_shrunk_rects:
        tangle.midtop = (window_size[0] / 2, 100)  # Place them near the middle of the window





    background=pg.Surface(window_size) #background surface
    background.fill((148,172,136))
    background.fill(background_color)
    # Below are the settings in order:
    # Animation speed, difficulty (white player) level, True or False playing 0-player
    # black player level, undo enabled, skip enabled, show legal moves enabled?
    speed_l,diff_l,single_bot,double_bot,p2_l,undo_on,skip_on,show_moves_on=pickle.load(open("settings.dat", 'rb'))
    changeSpeed(1.4 ** (speed_l - 5))   # Changes animation speed based on speed level
    line_length = 300                   # Length of settings slider line
    diff_h = 30                         # Height of difficulty slider
    p2_h=130                            # Height of white player slider
    speed_h = -120                      # Height of speed slider
    # Set players below, whether double bot, single bot, or no bot
    if double_bot:
        players=[bots[p2_l],bots[diff_l]]   # players=["human",bots[diff_l]]
    elif single_bot:
        players = ['human', bots[diff_l]]
    else:
        players = ['human',"human"]
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

    #Progress bar: surface with rectangle
    prog_bar_size=V((30,250))
    prog_bar=pg.Surface(prog_bar_size)
    prog_bar_rect=prog_bar.get_rect()
    prog_bar_rect.center=((board_width+3*window_size[0])/4,500)
    animating_prog_bar=False
    black_prog, white_prog=(0,0)

    #Making buttons!
    skip_button=Button((window_offset[0]-50,50),skip_button_color,"Skip",(20,20,20),skip_font)
    skip_button.midleft((10, window_size[1] / 2))
    undo_button=Button((window_offset[0]-50,50),undo_button_color,"Undo",(20,20,20),skip_font)
    undo_button.midleft((10, window_size[1] / 2-70))
    quit_button=Button((window_offset[0]-50,50),quit_button_color,'Quit',(20,20,20),skip_font)
    quit_button.midleft((10,window_size[1]/2+70))

    play_button=Button((250,70),play_button_color,"Play Game",play_text_color,play_font)
    play_button.center((window_size/2+V((0,110))))
    settings_button=Button((210,60),light_button_color,"Settings",(20,20,20),settings_button_font)
    settings_button.center((window_size/2+V((0,210))))

    size_strings=["{} x {}".format(i*2+4,i*2+4) for i in range(len(board_images))]
    board_size_buttons = [Button((100, 42),board_size_button_color,i,(40,40,40),board_size_font,thickness=1) for i in size_strings]
    for i, button in enumerate(board_size_buttons):
        button.center((window_size[0] / 2 + 250, 110 + i * 65)) #Place them on the board

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
        show_moves_button.changeText("Show Moves: OFF")

    # The sliders are just buttons with text shifted down
    slider_size=(12,30)
    slider_shift=V((0,27)) # This shifts the text down underneath the slider 25 pixels
    diff_slider=Button(slider_size,bubble_color,str(diff_l),slider_text_color,scale_font,thickness=1)
    diff_slider.center((window_size/2+((diff_l-5)*line_length/10,diff_h)))
    diff_slider.shiftText(slider_shift)
    p2_slider=Button(slider_size,bubble_color,str(p2_l),slider_text_color,scale_font,thickness=1)
    p2_slider.center((window_size/2+((p2_l-5)*line_length/10,p2_h)))
    p2_slider.shiftText(slider_shift)
    speed_slider=Button(slider_size,bubble_color,str(round(1.4 ** (speed_l - 5),1)),slider_text_color,scale_font,thickness=1)
    speed_slider.center((window_size/2+((speed_l-5)*line_length/10,speed_h)))
    speed_slider.shiftText(slider_shift)
    if speed_l>10: speed_slider.changeText("MAX") #In case the maximum speed is chosen

    # These are just plain text which we'll put on the screen
    # In game text:
    othello_box=TextBox("OTHELLO",othello_color,othello_font)
    othello_box.midtop((window_size[0]/2,10))
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

# Initialize Stuff
set_board_size(8)       # Set board up
clock=pg.time.Clock()   # pygame thing
no_moves = False        # Assume there are moves
game_active = False     # Start in the title screen
settings_open = False
left_clicking=None      # Not clicking on anything
game_over=False
blocked=True
counter=0               # Reset
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
                if not blocked:
                    if event.button == 1:
                        x,y = V(event.pos)-window_offset
                        # These are the GRID coords of the clicked pixel.
                        xspot = math.floor(x / sw)
                        yspot = math.floor(y / sw)
                        # This method checks if the clicked grid spot is a valid choice
                        if B.checkClick(xspot, yspot):
                            moveTo(xspot, yspot)  # If it's valid, we move to that spot
                            nextTurn()
                            blocked=True
                        elif (skip_on or no_moves) and skip_button.collidepoint(event.pos):
                            left_clicking = "skip"      # If allowed, skip selected
                        elif undo_on and undo_button.collidepoint(event.pos):
                            left_clicking = "undo"      # If allowed, undo selected
                        elif game_over and game_over_button.collidepoint(event.pos):
                            left_clicking = "game over"
                    elif event.button == 3:
                        if len(memory) > 1 and undo_on: #If allowed, undo on rightclick
                            undo()
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            elif event.type == pg.MOUSEBUTTONUP: #On upclick
                if event.button==1:
                    if left_clicking == 'skip' and skip_button.collidepoint(event.pos):
                        nextTurn() # If skip is selected, skip turn
                    elif left_clicking == "undo" and undo_button.collidepoint(event.pos):
                        if len(memory) > 1: #If undo is selected and we haven't gone too far back, undo.
                            undo()
                            blocked=True
                    elif left_clicking == "game over" and game_over_button.collidepoint(event.pos):
                        undo()
                        blocked=True
                    elif left_clicking == "quit" and quit_button.collidepoint(event.pos):
                        game_active = False # If quit is selected, go to title screen
                    left_clicking = None

        #####################################################################################
        elif settings_open:             # SETTINGS PAGE
            if event.type==pg.MOUSEBUTTONDOWN:
                if event.button==1: #Leftclick down
                    loc=event.pos
                    #Below are all the settings which could be selected.
                    if settings_button.collidepoint(loc):
                        left_clicking = 'close_settings'    # Select the "Close Settings" button
                    elif double_bot_button.collidepoint(loc):
                        left_clicking = "double bot"        # Select the "0 Player" button
                    elif single_bot_button.collidepoint(loc):
                        left_clicking='single bot'          # Select the "1 Player" button
                    elif no_bot_button.collidepoint(loc):
                        left_clicking = "no bot"            # "2 Player" button
                    elif undo_setting_button.collidepoint(loc):
                        left_clicking = "undo setting"      # "Undo: ON/OFF" button
                    elif skip_setting_button.collidepoint(loc):
                        left_clicking = "skip setting"      # "Skip: ON/OFF" button
                    elif show_moves_button.collidepoint(loc):
                        left_clicking = "show moves setting"
                    elif speed_slider.collidepoint(loc):
                        left_clicking = 'speed'             # Select the speed slider
                    elif (single_bot or double_bot) and diff_slider.collidepoint(loc):
                        left_clicking = 'difficulty'        # Difficulty slider
                    elif double_bot and p2_slider.collidepoint(loc):
                        left_clicking='p2'                  # Black bot slider
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            elif event.type==pg.MOUSEBUTTONUP:
                if event.button==1: #Leftclick up
                    if left_clicking=='close_settings' and settings_button.collidepoint(event.pos):
                        settings_open=False                 # Back to titles screen
                        settings_button.changeText("Settings")
                    elif left_clicking=='difficulty':       # Save slider data
                        new_center = (diff_l - 5) * line_length / 10 + window_size[0] / 2
                        diff_slider.centerx(new_center)  # Move the slider physically
                        data_dump()
                    elif left_clicking=='speed':            # Save slider data
                        data_dump()
                        new_center = (speed_l - 5) * line_length / 10 + window_size[0] / 2
                        speed_slider.centerx(new_center)
                    elif left_clicking=="p2":               # Save slider data
                        new_center = (p2_l - 5) * line_length / 10 + window_size[0] / 2
                        p2_slider.centerx(new_center)  # Move the slider physically
                        data_dump()
                    elif left_clicking=="double bot" and double_bot_button.collidepoint(event.pos):
                        double_bot=True                     # Change player lineup
                        single_bot=False
                        players[0] = bots[p2_l]             # 2 bots playing
                        players[1] = bots[diff_l]
                        no_bot_button.changeColor(light_button_color)
                        single_bot_button.changeColor(light_button_color)
                        double_bot_button.changeColor(dark_button_color) #This button is selected, so its a different color
                        data_dump()
                    elif left_clicking=='no bot' and no_bot_button.collidepoint(event.pos):
                        single_bot=False                    # Change player lineup
                        double_bot=False
                        players[0]="human"                  # 2 humans playing
                        players[1]="human"
                        double_bot_button.changeColor(light_button_color)
                        single_bot_button.changeColor(light_button_color)
                        no_bot_button.changeColor(dark_button_color) # This button is different color
                        data_dump()
                    elif left_clicking=='single bot' and single_bot_button.collidepoint(event.pos):
                        single_bot=True                     #Change player lineup
                        double_bot=False
                        players[0]='human'                  # Robot vs human
                        players[1]=bots[diff_l]
                        double_bot_button.changeColor(light_button_color)
                        no_bot_button.changeColor(light_button_color)
                        single_bot_button.changeColor(dark_button_color) #This button is different color
                        data_dump()
                    elif left_clicking=='undo setting' and undo_setting_button.collidepoint(event.pos):
                        undo_on=not undo_on                 #Swap whether undo is on or off
                        if undo_on:                         #If on, it should be selected and say on
                            undo_setting_button.changeColor(dark_button_color)
                            undo_setting_button.changeText("Undo:  ON")
                        else:                               #If off, it should be unselected and say off
                            undo_setting_button.changeColor(light_button_color)
                            undo_setting_button.changeText("Undo: OFF")
                        data_dump() #Save Settings data
                    elif left_clicking=='skip setting' and skip_setting_button.collidepoint(event.pos):
                        skip_on=not skip_on                 #Swap whether skip is enabled or not
                        if skip_on:                         # If on, should be selected and say on
                            skip_setting_button.changeColor(dark_button_color)
                            skip_setting_button.changeText("Skip:  ON")
                        else:                               # If off, should be unselected and say off
                            skip_setting_button.changeColor(light_button_color)
                            skip_setting_button.changeText("Skip: OFF")
                        data_dump() #Save Settings data
                    elif left_clicking=='show moves setting' and show_moves_button.collidepoint(event.pos):
                        show_moves_on=not show_moves_on                 #Swap whether showing moves is enabled or not
                        if show_moves_on:                         # If on, should be selected and say on
                            show_moves_button.changeColor(dark_button_color)
                            show_moves_button.changeText("Show Moves:  ON")
                        else:                               # If off, should be unselected and say off
                            show_moves_button.changeColor(light_button_color)
                            show_moves_button.changeText("Show Moves: OFF")
                        data_dump() #Save Settings data
                    left_clicking=None
        #####################################################################################
        else:                           # TITLE PAGE
            if event.type==pg.MOUSEBUTTONDOWN:
                if event.button==1: #Leftclick down
                    if play_button.collidepoint(event.pos):
                        left_clicking = 'play'          # Play button selected
                    elif settings_button.collidepoint(event.pos):
                        left_clicking = 'open_settings' # Settings button selected
                    else:
                        for i, but in enumerate(board_size_buttons):
                            if but.rect.collidepoint(event.pos):
                                left_clicking = "sizing" + str(i) # Boardsize button selected
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            elif event.type==pg.MOUSEBUTTONUP:
                if event.button==1: #Leftclick up
                    if left_clicking=='play' and play_button.collidepoint(event.pos):
                        game_active = True          # Start the game.
                        set_board_size(boardSize)   # This does some initialization
                        scores = [2, 2]             # Each player starts with 2 tiles
                        updateScores()
                    elif left_clicking=="open_settings" and settings_button.collidepoint(event.pos):
                            settings_open=True      # Open settings
                            settings_button.changeText(text="Close Settings")
                    elif left_clicking and left_clicking[:-1]=="sizing":
                        i=int(left_clicking[-1])    # Finds which size is being selected
                        if board_size_buttons[i].rect.collidepoint(event.pos): # If still selected, change board
                            set_board_size(i*2+4) #Reinitialize everything with new board size
                            updateTileList(B)
                    left_clicking=None #upclick means nothing's clicked
    ###########################################################################################################
    ###########################################################################################################
    # No matter what, we always have the background and OTHELLO
    screen.blit(background, (0, 0))
    othello_box.blit(screen)
    if game_active:
        quit_button.blit(screen,left_clicking=='quit') #Quit button, highlighted if selected
        if skip_on or no_moves: skip_button.blit(screen,left_clicking=='skip') # Skip if enabled
        if undo_on: undo_button.blit(screen,left_clicking=='undo') # Undo if enabled

        screen.blit(board_image,board_image_rect)               # Draw board
        screen.blit(prog_bar,prog_bar_rect)                     # Progress bar
        rect=pg.Rect((0,0),(V((1,1))+prog_bar_rect.size))
        rect.topright=prog_bar_rect.topright
        pg.draw.rect(screen,(0,0,0),rect,2)         # Progress bar outline

        if not blocked and players[turn] != 'human' and not game_over: # If its a robot's turn, let the robot play
            blocked=True #Don't bother the robot
            roboTurn(players[turn]) # Robot makes a move
            blocked=False

        if animating_prog_bar:
            animate_prog_bar()
        # Below, all of the tiles are animated
        blocked=False
        mult=4
        iii=0
        for row in tile_list:
            for tile in row:
                if tile!=None:
                    if tile.update():
                        blocked=True #If any tile is animating, some clicking is blocked
                    if tile.rect.width>0: #If the tile is too thin, it throws an error
                        pg.gfxdraw.filled_ellipse(screen, *tile.coords(), tile.color)  # Draw the filling
                        pg.gfxdraw.aaellipse(screen,*tile.coords(),tile.color) #Draw the smooth outline
                    else:
                        pg.draw.ellipse(screen,tile.color,tile.rect) #Draw a rougher circle sometimes
        if show_moves_on and not blocked:
            for move in B.legalMoves(): # For all legal moves, draw a circle highlighting the position
                pos=(window_offset+(V(move)+(0.5,0.5))*sw).intify()
                pg.gfxdraw.aaellipse(screen,*pos,int(sw*(1-tile_spacing)/2),int(sw*(1-tile_spacing)/2),(0,0,0))

        for tile in tiles_to_remove: # These tiles are out of the main list but are still disappearing
            blocked=True # Animations are occurring
            pg.draw.ellipse(screen,tile.color,tile.rect) # Animate the disappearing ellipse
            if not tile.update():
                tiles_to_remove=[]   # If the tiles are done removing, clear the list

        #                                       DRAWING TEXT
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        white_score_box.blit(screen)                                # Score writers
        black_score_box.blit(screen)
        scores_box.blit(screen)
        turn_box.blit(screen)
        if game_over:
            game_over_button.blit(screen,left_clicking=="game over")
        ######################################################################################################
        # JUST IN CASE, every 2 seconds or so, the tiles get fixed so they match the board.
        if counter==120:
            if not blocked:
                updateTileList(B)
            counter=0
        counter+=1
    else:
        settings_button.blit(screen,left_clicking in ('open_settings','close_settings'))
        ######################################################################################################
        if settings_open:
            #Drawing a bunch of buttons on the screen.
            double_bot_button.blit(screen,left_clicking=="double bot")
            no_bot_button.blit(screen, left_clicking=="no bot")
            single_bot_button.blit(screen,left_clicking=="single bot")
            undo_setting_button.blit(screen,left_clicking=="undo setting")
            skip_setting_button.blit(screen,left_clicking=="skip setting")
            show_moves_button.blit(screen,left_clicking=="show moves setting")
            speed_label_box.blit(screen)
            #Slider line for speed setting
            pg.draw.line(screen,(0,0,0),window_size/2+(-line_length/2,speed_h),window_size/2+(line_length/2,speed_h),2)
            if single_bot or double_bot:
                #Slider line for white bot setting
                pg.draw.line(screen,(0,0,0),window_size/2+(-line_length/2,diff_h),window_size/2+(line_length/2,diff_h),2)
                diff_slider.blit(screen, left_clicking == 'difficulty') #Draw slider
                if left_clicking == 'difficulty':           # If slider is selected
                    x_pos = pg.mouse.get_pos()[0]           # Approximate mouse postion to set difficulty
                    diff_l = max(min(round((x_pos - window_size[0] / 2) * 10 / line_length + 5), 10), 0)
                    diff_slider.changeText(str(diff_l))     # Change the text appropriately
                    players[1] = bots[diff_l]               # Set the bot to be a player
                    new_center= min(max(x_pos,window_size[0]/2-line_length/2),window_size[0]/2+line_length/2)                                                                                   # TBD
                    diff_slider.centerx(new_center)         # Move the slider physically
            if single_bot:
                diff_label_box.blit(screen)                         # Write difficulty on the screen
            if double_bot:
                p1_label_box.blit(screen)                           # Write white player on the screen
                p2_label_box.blit(screen)                           # Write black player on the screen
                pg.draw.line(screen, (0, 0, 0), window_size / 2 + (-line_length / 2, p2_h),
                             window_size / 2 + (line_length / 2, p2_h), 2)  # Line for p2 slider
                p2_slider.blit(screen,left_clicking=='p2')                  # Draw p2 Slider
                if left_clicking=="p2":
                    x_pos = pg.mouse.get_pos()[0]                   # Approximate mouse pos gets p2 skill lvl
                    p2_l = min(max(round((x_pos - window_size[0] / 2) * 10 / line_length + 5),0),10)
                    p2_slider.changeText(str(p2_l))
                    new_center=min(max(x_pos,window_size[0]/2-line_length/2),window_size[0]/2+line_length/2)                                                                                    #TBD
                    p2_slider.centerx(new_center)
                    players[0] = bots[p2_l]             # Set black player
            if left_clicking=='speed':
                x_pos = pg.mouse.get_pos()[0]  # use mouse position to set speed
                speed_l=max(round((x_pos-window_size[0]/2)*10/line_length+5),0)
                if speed_l>10 and speed_l<11:  # Speed lvl 12 is the secret max lvl
                    speed_l=10
                if speed_l>=11:
                    speed_l=11
                    changeSpeed(100000)                 # Max speed
                    speed_slider.changeText("MAX")
                    new_center = window_size[0]/2+line_length*0.6
                else:
                    changingspeed = 1.4 ** (speed_l-5)  # Set speed and text
                    speed_slider.changeText(str(round(changingspeed,1)))
                    changeSpeed(changingspeed)          # Change tile animations
                    new_center = min(max(x_pos,window_size[0]/2-line_length/2),window_size[0]/2+line_length/2)
                speed_slider.centerx(new_center)        # Move slider
            speed_slider.blit(screen,left_clicking=="speed") # Draw slider
        else:   # TITLE SCREEN
            screen.blit(board_image_shrunk,board_image_shrunk_rect) # Show little board drawing
            play_button.blit(screen,left_clicking=='play')          # Play button
            for i,but in enumerate(board_size_buttons):             # Board sizing buttons
                but.blit(screen,left_clicking=="sizing{}".format(i))
    pg.display.update()
    clock.tick(60) # Limits to 60 fps