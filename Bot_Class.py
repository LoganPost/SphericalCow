"""
This is the Robot class. Robot objects hold information about their decision making strategies and the
functions dictate the decision making process according to these paramters
 - Parameters include:
    () Preference to take Corners and Edges (score multiplier)
    () Patience for skipping repeatedly before eventually just making a move
    () Whether to actually think or just choose randomly
    () How far ahead to look in the game (0 is just counting tiles on the board)
- Thought process includes:
    () Count the tiles on the board (with multiplier)
    () Assuming the opponent will make the best move, find the *long term* utility of a move by above metric
    () Knowing long term utilities, choose the best move given a board setup
"""
debug=False

from Board_Class import Board
from Vector_Class import V
import random
class Bot():
    def __init__(self,edgeX=1,cornX=1,depth=0,name="NamelessBot",patience=4,RANDOM=False):
        if debug: # Preconditions: Patience must be an natural number of moves and depth must be positive
            assert depth>=0
            assert isinstance(patience,int) and patience>0
        self.name=name   # Name is just for fun
        #In calculating fitness, it is more beneficial to prioritize edges and corners.
        self.edgeX=edgeX # Edge fitness multiplier
        self.cornX=cornX # Corner fitness multiplier
        self.depth=depth #How many iterations to think foreward
        self.patience=patience  #How many times can we say undo until we do something else.
        self.RANDOM=RANDOM
    def __str__(self): # Introduce yourself
        return "I am a robot named {} with skill level {}.".format(self.name,int((self.depth+1)*self.edgeX),self.cornX,self.edgeX)
    def details(self): # Provide details
        return "My name is {} and I have depth {}. I give corners value {} and edges value {}.".format(
            self.name, self.depth, self.cornX, self.edgeX)
    def pureUtility(self,board): #This is surface level board utility.
        if debug: #Preconditions: square board with the right values
            for i in board:
                for j in i:
                    assert j in (0,1,-1)
            assert len(board)==len(board[0])
        # This looks, with no strategy, at the goodness of the board position
        # We count up all the pieces on your side minus all the pieces on the opponents side including multipliers
        iHaveTiles=False                        # Assume you have no tiles
        theyHaveTiles=False                     # Assume they have no tiles
        for row in board:
            for i in row:
                if i==1:                        # If you find a tile, you have one
                    iHaveTiles=True
                if i==-1:                       # Found a tile for opponent
                    theyHaveTiles=True
        board_len=len(board)
        if not iHaveTiles:                      # If you have no tiles, this is REALLY BAD
            return -1*board_len*board_len*self.cornX
        if not theyHaveTiles:                   # If they have no tiles, this is REALLY GOOD
            return 1 * board_len * board_len * self.cornX
        utility=0
        # Now, we iterate through the board and add up the points, with multipliers
        for yCord,row in enumerate(board):
            for xCord, el in enumerate(board):
                valHere=board[yCord][xCord]
                #This checks if the position is an edge or corner
                xEdge=xCord==board_len-1 or xCord==0
                yEdge=yCord==board_len-1 or yCord==0
                if xEdge or yEdge:
                    if xEdge and yEdge:
                        #If the position is a corner, we give a point multiplier(positive or negative)
                        #based on the corner multiplier
                        utility+=valHere*self.cornX
                    else:
                        #For edges, we use the edge multiplier
                        utility+=valHere*self.edgeX
                else:
                    #Otherwise, the utility goes up or down by 1 if the position is ours.
                    utility+=valHere
        return utility
    def utility(self,board,depth): #This gets the clever utility of the board position
        if debug: # Preconditions: depth must be natural, square board with the right values
            isinstance(depth,int) and depth>=0
            for i in board:
                for j in i:
                    assert j in (0,1,-1)
            assert len(board)==len(board[0])
        #This utility is recursive, and evaluates the board quality given that
        # it's the opponents turn. This means we'll evaluate this function after a potential move.
        if depth==0:
            # At 0 depth, we just look at the surface level quality of the board
            # this is the base case for recursion.
            return self.pureUtility(board)
        else:
            # If depth is more than zero, we evaluate the opponent's decision making.
            # The opponent will be working with the inverted board position:
            OppBoard = board.inverted()
            #The opponent has a set of possible moves on this board.
            OppMoves=OppBoard.legalMoves()
            #If we're predicting the opponents move, this means we're
            # thinking with a depth 1 more than them.
            OppDep=depth-1
            # We assume that they will also choose utility which is maximized
            # This means that they'll look at the utility of all moves, or passing, and choose the max.
            OppUt=max([self.utility(OppBoard.placeTile(*move)[0], OppDep) for move in OppMoves] + [self.utility(OppBoard, OppDep)])
            if debug: # Postcondition: Correct opponent's utility which is at least as good as doing nothing
                assert isinstance(OppUt,int) and OppUt>=self.utility(OppBoard,OppDep)
            # Whatever utility they see, we'll see the opposite.
            return -1*OppUt
        pass
    def chooseMove(self,board,passAllowed=True):
        if debug: # Precondition: square board with good values
            for i in board:
                for j in i:
                    assert j in (0,1,-1)
            assert len(board)==len(board[0])
        if self.RANDOM:
            moves=list(board.legalMoves())
            if moves:
                return random.choice(moves)
            else:
                return (-5,-5)
        depth=random.choice((int(self.depth),int(self.depth+.5)))
        #-5 is our keyword default, meaning that no move beats the utility of just passing.
        bestMove = (-5, -5)
        #If passing is allowed, (based on patience), we say that the utility of default(passing)
        # is the utility of the current board.
        if not (board.inverted()).areLegalMoves():
            #If inverting the board gives the opponent no legal moves, there's no point in passing.
            passAllowed=False
        if passAllowed:
            bestMoveUtility = self.utility(board,depth)
        else:
            #If passing is not allowed, this utility should be the WORST possible case. (all enemies)
            bestMoveUtility=self.pureUtility(Board([[-1 for i in row]for row in board]))
        #Now we look through all legal moves and compare them to our best case (or default case)
        for move in board.legalMoves():
            #The move quality is the utility of the board after going there.
            moveUtility = self.utility(board.placeTile(*move)[0],depth)
            if moveUtility > bestMoveUtility: #If we have a new best, dethrone the best.
                bestMoveUtility = moveUtility
                bestMove = move
            #elif moveQuality == bestMoveUtility and random.random() > .7:
                #If two moves are equal, we want to pick somewhat randomly which one.
            #    bestMove = move
        if debug: # Move is legal or nothing
            if bestMove!=(-5,-5):
                assert board.isLegal(*bestMove)
        return bestMove
