"""
These classes are useful for the creating visual effects.
 - Tile class holds information about the color, location, shape, and animation state of each Tile
    () The Board holds all information about the actual game, but the tiles are the only thing the player
       can actually see.
    () There are three animations which morph the dimensions of the tile: Placing, Flipping, and Removal.

 - Button class helps to concisely describe and display a clickable button on the screen.
    () Buttons have dimensions, location, color, text, font, text color, text location, border. This would
       otherwise require a bunch of different variables and assignments.
    () Also, it takes only one line of code display a button, which would otherwise take six
"""
debug=False

import pygame as pg
from Vector_Class import V

board_width=500
tile_spacing=0.12
pg.init()
# window_size=V((800,650))
window_size=V((800,650))
board_dimension=V((board_width,board_width))
window_shift=(window_size-board_dimension)/2
# colors = [(33,33,33), (175,175,175)]
colors = [(25,25,25), (175,175,175)]
import math
class Tile():
    def __init__(self,x,y,color_index,sw):
        if debug: # Preconditions: x and y are board positions, color_index is 0 or 1
            assert color_index in (0,1)
            assert 0<=x<round(board_width/sw)
            assert 0<=y<round(board_width/sw)
            assert x==int(x)
            assert y==int(y)
        super().__init__()
        self.sw=sw
        self.x=x
        self.y=y
        self.window_position=window_shift+V((sw*(x+0.5),sw*(y+0.5)+50))
        self.rect=pg.Rect(0,0,sw*(1-tile_spacing),sw*(1-tile_spacing))
        self.rect.center=self.window_position
        self.color_index = color_index # This is relevant data. Color is either 0 or 1.
        self.color=colors[self.color_index]
        self.place()
        self.flipping=False
        self.removing=False
        if debug: # Postconditions: It's placing now and the color is legal
            assert self.placing==True
            assert self.placing_t==0
            assert self.color in colors
    def place(self): # Put a tile down
        #The piece accelerates towards the board.
        self.placing=True
        self.placing_t=0
    def place_animation(self):
        if debug: #Preconditions: We are placing, the time is appropriate
            assert 0<=self.placing_t<placing_tmax
            assert self.placing==True
        sw=self.sw              # Square width
        self.placing_t += 1     # Time increases
        scale = (2 - (self.placing_t / placing_tmax) ** 2) * sw * (1 - tile_spacing) # Piece falls towards the board
        self.rect = pg.Rect(0, 0, scale, scale)     # Resize the rectangle
        self.rect.center = self.window_position     # Recenter the rectangle
        if self.placing_t >= placing_tmax:          # Reached the end of the placing animation
            self.placing = False
            self.rect = pg.Rect(0, 0, sw * (1 - tile_spacing), sw * (1 - tile_spacing)) # Final resizing
            self.rect.center = self.window_position                                     # Final recentering
        if debug: # Postconditions: we're either still flipping or done
            assert 0<self.placing_t<placing_tmax or not self.placing
        pass
    def coords(self): # Accesses the x,y,w,h dimensions of the tile ellipse
        return (*self.rect.center,int(self.rect.width/2),int(self.rect.height/2))
    def flip(self): # Turn the tile over
        self.flipping=True
        self.must_flip_color=True # Waiting to flip the color until it's time
        self.flipping_t=0
    def flip_animation(self):
        if debug: #Preconditions: We are flipping, the time is appropriate, and the rectangle is centered
            assert 0<=self.flipping_t<flipping_tmax
            assert self.flipping==True
        sw=self.sw              # Square width
        self.flipping_t += 1    # Time increases
        scale = (self.flipping_t / (flipping_tmax ** 2) * (flipping_tmax - self.flipping_t) * 3 + 1) * sw * (
                    1 - tile_spacing) # The piece jumps up to flip over (quadratic)
        # Below, we use cosine to show rotation in addition to the jumping rescaling
        self.rect = pg.Rect(0, 0, scale * math.cos(self.flipping_t / flipping_tmax * math.pi), scale)
        self.rect.center = self.window_position     # Recenter
        # BELOW is the only relevant change to the data of the piece.
        if self.must_flip_color and self.flipping_t > flipping_tmax / 2:
            self.color_index = (self.color_index + 1) % 2   # Switch color index
            self.color = colors[self.color_index]           # Set color
            self.must_flip_color = False                    # We flipped the color, so we're done with that
        if self.flipping_t >= flipping_tmax:                # At the end of the flip
            self.flipping = False                           # Stop flipping
            self.rect = pg.Rect(0, 0, sw * (1 - tile_spacing), sw * (1 - tile_spacing)) #Final rescale
            self.rect.center = self.window_position         # Final Recenter
        if debug: # Postconditions: Rect is still centered. We changed the colors if necessary
            assert self.must_flip_color==False or self.flipping<=flipping_tmax / 2
        pass
    def remove(self): # Pick the piece off the board
        self.removing=True
        self.removing_t=0
    def remove_animation(self):
        if debug: #Preconditions: We are removing, the time is appropriate, and the rectangle is centered
            assert 0<=self.removing_t<placing_tmax
            assert self.removing==True
        sw=self.sw                          # Square width
        self.removing_t += 1                # Time increases
        t = self.removing_t / placing_tmax  # Percentage of animation
        scale = sw * (1 - tile_spacing)     # Scale is normal
        theta = (math.pi / 2 * t ** 2)      # The rotation angle increases
        shift = -((t + t ** 2) / 2) * sw    # shift center up over time
        self.rect = pg.Rect(0, 0, scale * math.cos(theta), scale)   # Rescale
        self.rect.center = self.window_position + V((0, shift))     # Recenter
        if self.removing_t >= placing_tmax: # When time's up, stop the animation
            self.removing = False
    def update(self): # Check if animiations are necessary, and run them.
        if self.flipping:
            self.flip_animation()
        if self.placing:
            self.place_animation()
        if self.removing:
            self.remove_animation()
        return self.flipping or self.placing or self.removing

rad=10 # Corner radius of buttons
class Button():
    def __init__(self,size,color,text="",text_color=(0,0,0),font=pg.font.SysFont('calibri', 20),thickness=2):
        if debug: # Preconditions: parameters must be the right type
            assert len(size)==2
            assert len(color)==3
            for i in color:
                assert 0<=i<256
            assert isinstance(text,str)
            assert len(text_color)==3
            for i in text_color:
                assert 0<=i<256
            assert isinstance(thickness,int)
        self.font=font                                      # Font of text
        self.thickness=thickness                            # Thickness of border
        self.color=color                                    # Color of fill
        self.text_color=text_color                          # Color of text
        self.text=text                                      # Words to print
        self.rect=pg.Rect(0,0,*size)                        # Dimensions of button
        self.text_surface=font.render(text,True,text_color) # Rendering text onto surface
        self.text_rect=self.text_surface.get_rect()         # Used for centering text surface
        self.text_shift=V((0,0))                            # Used to shift text off center
        if debug: # Postconditions: The rects should be in same place
            assert self.rect.topleft==self.text_rect.topleft
    def changeColor(self,color):
        self.color=color    # Changes color lol
    def changeText(self,text=None,color=None,font=None):    # Changes some properties about the text
        if debug: # Preconditions: Check for correct type. Not dealing with font
            if text!=None:
                assert isinstance(text,str)
            if color!=None:
                assert isinstance(color,tuple) and len(color)==3
        if text!=None:
            self.text=text          # Change the words
        if color!=None:
            self.text_color=color   # Change color of the text
        if font!=None:
            self.font=font          # Change the font
        self.text_surface=(self.font).render(self.text,True,self.text_color)    # Redraw text surface
        self.text_rect=self.text_surface.get_rect()                             # New Rect for centering
        self.text_rect.center=self.rect.center+self.text_shift                  # Center the text
        # No Postconditions necessary
    def blit(self,surf,clicking):   # Draws the button on the screen, bolder if selected
        if debug: # Preconditions: Correct input types, text is right
            assert isinstance(clicking,bool)
            assert self.text_rect.center==self.rect.center+self.text_shift
        pg.draw.rect(surf,self.color,self.rect,border_radius=rad)   # Draw background
        surf.blit(self.text_surface,self.text_rect)                 # Write text
        if clicking: # Draw the button border; make it thicker if the button is being pressed.
            pg.draw.rect(surf, V(self.color)/3, self.rect, self.thickness*2,border_radius=rad)
        else:
            pg.draw.rect(surf, V(self.color)/3, self.rect, self.thickness,border_radius=rad)
    def midleft(self,loc): # Move button by setting the midleft point
        self.rect.midleft=loc   # Move rect
        self.text_rect.center=self.rect.center+self.text_shift  # Recenter text (with shift)
    def center(self,loc): # Move button by setting the center point
        if debug:
            assert isinstance(loc,tuple) and len(loc)==2
        self.rect.center=loc    # Move rect
        self.text_rect.center=loc+self.text_shift               # Recenter text (with shift)
    def centerx(self,pos): # Move the central x coord of the button
        if debug:
            assert isinstance(pos,int) or isinstance(pos,float)
        self.center((pos,self.rect.centery)) # Keep centery where it is, move to new x
    def shiftText(self,shift=(0,0)): #Shift the text off the the center of the button
        if debug:
            assert isinstance(shift,tuple) and len(shift)==2
        self.text_shift=shift
        self.text_rect.center = V(shift)+self.text_rect.center # Center the text off the button's center
    def collidepoint(self,point):   # Check for collision
        if debug:
            assert isinstance(point,tuple) and len(point)==2
        return self.rect.collidepoint(point)

class TextBox():
    def __init__(self,text="",color=(0,0,0),font=pg.font.SysFont('calibri',20)):
        self.font=font                                      # Font of text
        self.color=color                                    # Color of text
        self.text=text                                      # Words to print
        self.surf=font.render(text,True,color) # Rendering text onto surface
        self.rect=self.surf.get_rect()                      # Dimensions of textbox
        self.middle=self.rect.center
    def center(self,pos):
        self.rect.center=pos
        self.middle = self.rect.center
    def midtop(self,pos):
        self.middle=pos
        self.rect.midtop=pos
        self.middle=self.rect.center
    def changeText(self,text=None,color=None,font=None):
        if text!=None:
            self.text=text          # Change the words
        if color!=None:
            self.color=color   # Change color of the text
        if font!=None:
            self.font=font          # Change the font
        self.surf=self.font.render(self.text,True,self.color)
        self.rect=self.surf.get_rect()
        self.center(self.middle)
    def blit(self,screen):
        screen.blit(self.surf,self.rect)
def changeSpeed(newSpeed): # Change the animation speed.
    if debug: #Can't have non-positive speed
        assert newSpeed>0
    global flipping_tmax,placing_tmax
    flipping_tmax = 20 / newSpeed
    placing_tmax = 15 / newSpeed
