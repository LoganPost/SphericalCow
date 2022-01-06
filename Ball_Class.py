from Vector_Class import V
import pygame as pg
pg.init()
from pygame import gfxdraw

class Ball():
    def __init__(self, pos=(300,300), vel=(0,0), mass=1, rad=10,color=(255,0,0),image=None):
        self.pos = V(pos);
        self.vel = V(vel);
        self.mass = mass;
        self.rad = int(rad);
        self.rect=pg.Rect(0,0,int(rad)*2,int(rad)*2)
        self.color=color
        self.image=image
        if image!=None:
            self.rect=image.get_rect()
            self.image=pg.transform.rotozoom(image,0,rad*4/(self.rect.width+self.rect.height))
            self.rect=self.image.get_rect()
        self.rect.center=self.pos
    def ball_collision(self, ball,e):
        # convenience, describing position
        pos1 = V(self.pos)
        pos2 = V(ball.pos)
        # connection vector is the Normal of the collision, normalized
        connect = (pos2-pos1).normalize()
        ##print("Normalized Connection ",end="")
        #        connect.show()
        # This gives me the normal component and perp component. The perp component
        # will be unaffected, while the normal component will behave like a typical
        # elastic collision
        nty=V((0,1))
        norm_1 = connect*self.vel
        perp_1 = connect.cmul(nty)*self.vel
        norm_2 = connect*ball.vel
        perp_2 = connect.cmul(nty)*ball.vel
        # THIS EQUATION solves the elastic colision for the New ncomponent
        v1=norm_1
        v2=norm_2
        mr=ball.mass/self.mass
        norm_2_ref=((1+e)*v1-(e-mr)*v2)/(1+mr)
        mr=self.mass/ball.mass
        norm_1_ref=((1+e)*v2-(e-mr)*v1)/(1+mr)

        # Now I reparamatrize the new components as x and y using the conjugate of connect (which is the inverse)
        xvel1N = V((norm_1_ref, perp_1))*connect.conj()
        yvel1N = V((norm_1_ref, perp_1))*connect.conj().cmul(nty)

        xvel2N = V((norm_2_ref, perp_2))*connect.conj()
        yvel2N = V((norm_2_ref, perp_2))*connect.conj().cmul(nty)

        self.vel = V((xvel1N, yvel1N))
        ball.vel = V((xvel2N, yvel2N))
        # self.pos += self.vel.scale(step * (1 - elastic))
        # ball.pos += ball.vel.scale(step * (1 - elastic))

        # self.vel = V(V(ncomp1N * elastic, pcomp1)*connect.conj(),
        #                V(ncomp1N * elastic, pcomp1)*connect.conj().cmul(nty))
        # ball.vel = V(V(ncomp2N * elastic, pcomp2).dot(connect.conj()),
        #                Vec(ncomp2N * elastic, pcomp2).dot(connect.conj().complexMult(Vec(0, 1))))

        return;
    def walls(self,xmin,ymin,xmax,ymax,e):
        if (self.pos[0] <= self.rad + xmin and self.vel[0] < 0):
            self.vel *= (-e, 1)
            self.pos=V((xmin+self.rad,self.pos[1]))
        elif (self.pos[0] >= xmax - self.rad and self.vel[0] > 0):
            self.vel*=(-e,1)
            self.pos = V((xmax-self.rad, self.pos[1]))
        if (self.pos[1] <= self.rad + ymin and self.vel[1] < 0):
            self.vel *= (1, -e)
            self.pos=V((self.pos[0],ymin+self.rad))
        elif (self.pos[1] >= ymax - self.rad and self.vel[1] > 0):
            self.vel*=(1,-e)
            self.pos = V((self.pos[0], ymax-self.rad))
        pass
    def check_ball_collision(self, ball):
        return (self.pos.dist(ball.pos) <= self.rad + ball.rad) and (self.vel-ball.vel)*(ball.pos-self.pos)>=0
    def move(self,stepsize):
        self.pos+=self.vel*stepsize
        self.rect.center=self.pos.intify()
    def blit(self,screen):
        if self.image==None:
            gfxdraw.filled_circle(screen,*self.pos.intify(),self.rad,self.color) # (screen,self.color,self.rect)
            gfxdraw.aacircle(screen,*self.pos.intify(),self.rad,self.color)
        else:
            screen.blit(self.image,self.rect)
    def goto(self,pos):
        self.pos=V(pos)
        self.rect.center=pos
    def kinetic_energy(self):
        return self.mass*self.vel.squarelen()
    def accelerate(self,vec):
        self.vel+=vec
    pass;
class Player(Ball):
    pass