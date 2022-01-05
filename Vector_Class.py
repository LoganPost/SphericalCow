"""
 - This class V is a vector subclass of tuples. It allows me to add coordinates pointwise, mutliply
   and divide them, and generally do nice things with them.
 - This class is just generally useful to me and is a little overcomplicated for just Othello
   I just think it is useful in general.
 - I don't have pre/post-conditions for this class; I see it more as adjacent to the final project
"""
import math

class V(tuple):
    def __add__(self,other): #Adds vectors pointwise
        return V(self[i]+other[i] for i in range(len(self)))
    def __sub__(self,other): #Subtract vectors pointwise
        return V(self[i] - other[i] for i in range(len(self)))
    def __mul__(self,other): # Multiplication
        #For vector and number, just scale
        if isinstance(other,int) or isinstance(other,float):
            return V(i*other for i in self)
        else: # For 2 vectors, dot product
            return sum(self[i]*other[i] for i in range(len(self)))
    def __rmul__(self,other): # Commutative multiplication
        return self*other
    def __truediv__(self,other): #Division
        # For vector and number, just scale
        if isinstance(other,int) or isinstance(other,float):
            return V(i/other for i in self)
        else: # For 2 vectors, dot product-ish, where other is upsidedown
            return sum(self[i]/other[i] for i in range(len(self)))
    def pmul(self,other): # Pointwise multiplication
        return V(self[i]*other[i] for i in range(len(self)))
    def cmul(self,other):
        return V((self[0]*other[0]-self[1]*other[1],self[0]*other[1]+self[1]*other[0]))
    def cross(self,other): #Cross product
        if len(self)!=3: #Only length 3 vectors can take cross product
            return "This vector can't have cross product, it is length "+str(len(self))
        i=self[1]*other[2]-self[2]*other[1]
        j=self[2]*other[0]-self[0]*other[2]
        k=self[0]*other[1]-self[1]*other[0]
        return V(i,j,k) #Cross prod formula
    def __abs__(self): #Get pythagorian length of vector
        return (sum(i**2 for i in self))**(1/2)
    def __rsub__(self,other): #Commutative-ish subtraction
        return (-1)*(self-other)
    def __radd__(self,other): #Commutative addition
        return self+other
    def __iadd__(self,other): # Different format of adding
        return self+other
    def __isub__(self,other):
        return self-other
    def intify(self): #Turns each element to an int
        return V((int(i) for i in self))
    def conj(self):
        return V((self[0],-self[1]))
    def dist(self,other):
        return abs(other-self)
    def __imul__(self,other):
        return self.pmul(other)
    def normalize(self):
        if abs(self)==0:
            return self
        return V((i/abs(self) for i in self))
    def squarelen(self):
        return sum([i**2 for i in self])
    def rotated(self,degrees):
        r=(math.cos(degrees),math.sin(degrees))
        return self.cmul(r)