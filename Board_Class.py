"""
 - The Board Class holds the game state (or hypothetical game states) at any time.
 - It is represented as a list of lists:
    () Each row is a list of ints indicated a friendly(1), enemy(-1), or no(0) tile
    () The Board itself is constructed as a list of rows.
 - The logic and rules of the game occur via these functions. These functions only work from the perspective
   of whoever's turn it is. Thus, "legalMoves()" tells you all of the moves for whoever is currently playing,
   and inverting the board allows you to see the moves for the other person
 - This board can be copied, reversed, and mutated according to game rules
"""
debug=False

class Board(list):
    def countTiles(self):
        #Total spaces minus empty spaces
        return len(self)*len(self)-self.emptySpaces()
    def show(self): #This is a way of displaying in text, using matrix form
        if debug:
            assert len(self)==len(self[0])
        for r,row in enumerate(self):
            out="["
            first=True
            for e,el in enumerate(row):
                if not first:
                    for i in range(4 - len(str(el))):
                        out += " "
                else:
                    first=False
                out+=str(el)
            out+="]"
            print(out)
        print()
    def inverted(self): # This gives the opposite of the board, letting us look from the opponents perspective
        return Board([[-1*j for j in i] for i in self]) #Accessor
    def invert(self): #This isnt working (mutator)
        for r,row in enumerate(self):
            for c,el in enumerate(row):
                assert self[r][c] == el
                self.show()
                print()
                if self[r][c] == 1:
                    self[r][c] = -1
                elif self[r][c] == -1:
                    self[r][c] = 1
                self.show()
    def placeTile(self,xCord,yCord): #This assumes the move is legal and makes the move.
        if debug:
            assert self.isLegal(xCord,yCord)
        board=self.copy()
        flips=[]
        #We have to find all possible sandwiches and report back the flips
        #All vertical, horizontal, and diagonal directions are combinations of these two lists.
        for vDir in [-1,0,1]:
            for hDir in [-1,0,1]:
                if board.checkForSandwich(xCord,yCord,hDir,vDir): #If there's a sandwich in this direction...
                    xLook, yLook = xCord + hDir, yCord + vDir
                    while board[yLook][xLook] == -1:
                        #While we move through the meet of the sandwich, we continue flipping tiles.
                        #We flip tiles as long as we're looking at enemy pieces.
                        board[yLook][xLook]=1       # Change to my piece
                        flips.append((xLook,yLook)) # Gotta flip this one
                        xLook += hDir
                        yLook += vDir
        board[yCord][xCord]=1
        if debug:
            assert len(flips)>0
            assert board[yCord][xCord]==1
        return board,flips #This gives the new board, but also the list of flips that we made.
    def copy(self):# Makes a copy
        return Board([[j for j in row] for row in self])
    def checkClick(self,xCord,yCord): #Checks if a click is allowed
        if debug:
            assert isinstance(xCord,int) and isinstance(yCord,int)
            for i in self: #Our elements are just 0,1, and -1
                for j in i:
                    assert j in (0,-1,1)
        #If we're inside the bounds of the grid
        if yCord<len(self) and yCord>=0:
            if xCord<len(self) and xCord>=0:
                #If the move is legal, we return true
                return self.isLegal(xCord,yCord)
        return False
    def isLegal(self,xCord,yCord):
        if debug:
            assert 0<=xCord<len(self) and 0<=yCord<len(self)
        # A move is only legal if we can find a sandwich. Thus, we search.
        if self[yCord][xCord]==0: #It can't already have a piece there...
            for vDir in [-1,0,1]:
                for hDir in [-1,0,1]:
                    #For all directions, if there's at least ONE sandwich, the move is legal
                    if self.checkForSandwich(xCord,yCord,hDir,vDir):
                        return True
        #If we found no sandwiches, the move is illegal.
        return False
    def checkForSandwich(self,xCord,yCord,hDir,vDir):
        if debug:
            assert isinstance(xCord,int) and isinstance(yCord,int)
            assert self[yCord][xCord]==0 #The spot should be empty
        xLook, yLook = xCord + hDir, yCord + vDir
        trivial=True #First, we assume that the sandwich has no contents, i.e. its trivial
        if yLook == len(self) or yLook == -1 or xLook == len(self) or xLook == -1:
            # If We're going to run off the edge of the grid, stop looking.
            return False
        while self[yLook][xLook] == -1: # While we are looking at enemy pieces:
            #While we're in the sandwich, we found some contents, so the sandwich is not trivial
            trivial=False
            xLook += hDir
            yLook += vDir
            if yLook==len(self) or yLook==-1 or xLook==len(self) or xLook==-1:
                #Make sure we didnt hit the end of the grid...
                return False
        if debug:
            assert self[yLook][xLook] == 1 or self[yLook][xLook] == 0
        #Once the sandwich is finished, we found a Sandwich ONLY IF:
            #It's not empty, a.k.a trivial
            #The other end of the sandwich is also a friendly piece.
        return self[yLook][xLook] == 1 and not trivial
    def legalMoves(self): #Finds ALL legal moves on the board
        #The bots will need to consider every possibility, so they'll ask for this generator
        for i in range(len(self)):
            for j in range(len(self)):
                if self.isLegal(i,j):
                    #If each spot is legal, we yield it.
                    yield (i,j)
    def emptySpaces(self): #Counts the empty spaces
        if debug: #PreCondition: All the elements should be 0,1, or -1
            assert len(self)==len(self[0])
            for i in self:
                for j in i:
                    assert j in (0,1,-1)
        count=0
        #This is a pretty clear function.
        for i in self:
            for j in i:
                if j==0:
                    count+=1
        if debug:
            assert 0<=count<=len(self)*len(self)
        return count
    def areLegalMoves(self): # Checks if there are any legal moves
        for i in range(len(self)):
            for j in range(len(self)):
                if self.isLegal(i,j):
                    if debug:
                        assert len(list(self.legalMoves()))!=0
                    #If any spot is legal, we say true
                    return True
        if debug: # Postcondition: If we haven't found a move, there isn't one, so the list of legal moves should be 0
            assert len(list(self.legalMoves()))==0
        return False
def set_up_board(size):
    if debug: # Precondition: The size of the board must a positive integer divisible by 2.
        assert size/2==int(size/2)
        assert size>0
    board = Board([[0 for j in range(size)] for i in range(size)]) # Construct the board
    mid = int(len(board) / 2 - 1)   # Get the middle of
    board[mid][mid] = 1             # Set the four tiles down
    board[mid][mid + 1] = -1
    board[mid + 1][mid + 1] = 1
    board[mid + 1][mid] = -1
    if debug:
        assert sum([sum(i for i in j) for j in board])==0 #The tiles should add up to 0
    return board