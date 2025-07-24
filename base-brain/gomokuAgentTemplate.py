import random
import numpy as np
from scipy import signal
import pisqpipe as pp
from pisqpipe import state
from structs import Point

pp.infotext = (
    'name="pbrain-geneticPeabrain", authors="Andrew Petten, Chance Kane, Jack Klobchar, Tim Xu"'
)
# genome for the genetic algorithm 11 values, 10 arbitrary, one constrained to [0,1]
# #genome = [zero-closed,zero-open,one-closed,one-open,two-closed,two-open,three-closed,three-open,four-closed,four-open, aggression] 
genome =  [8, 16, 32, 64, 128, 512, 1000, 2000, 0.5]  # genome for the genetic algorithm

MAX_BOARD = 100
#0 = empty, 1 = my stone, 2 = opponent's stone, 3 = winning move
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]
diagKernel = np.eye(9, dtype = np.int8)
diagKernel[4,4] = 0
antiDiagKernel = np.rot90(diagKernel)
verticalKernel = np.zeros_like(antiDiagKernel)
verticalKernel[:,4] = 1
verticalKernel[4,4] = 0
horizontalKernel = np.rot90(verticalKernel)
kernels = [diagKernel, antiDiagKernel, verticalKernel, horizontalKernel]
relevanceKernal = np.ones((9,9), dtype=np.int8) #used to track relevance of a point
directions = [[0,1],[1,1],[1,0]]
#possible alternatives for kernels: 8 compass directions? twice as many ops, but better for threats accurately

def clamp(value, min_val, max_val):
    """Clamps a single numerical value within a specified range."""
    return max(min(value, max_val), min_val)

#Generate and return a board mask indicating which positions are within relevance range of another piece
def identify_relevant_positions(board):
  relevantMask = np.zeros_like(board, dtype=int)  #create blank mask
  convolved = signal.convolve2d(board, relevanceKernal, mode='same', boundary='fill', fillvalue=0) #convolve board with 9*9 of 1s to render any point within 5 squares of a piece nonzero
  relevantMask = (convolved != 0)*1    #update mask to show locations within 5 of another piece
  return relevantMask

def calculate_value_at_point(board, x, y, maxLength = 4,player = 1):
  value = 0 
  lookup = np.array(genome[:-1])
  for direction in directions:
    i,j = x,y
    tilesInARow = 1; 
    lengthPos,lengthNeg = 0,0
    blocked = False

    for k in range(1,maxLength):  #crawl direction out to max length    
      i += direction[0]
      j += direction[1]
      if i < 0 or i >= len(board) or j < 0 or j >= len(board[0]):
        lengthPos = k-1
        blocked = True
        break
      if board[i][j] == 0:
        continue
      elif board[i][j] == player:  #if new piece of 
        tilesInARow+=1
      elif board[i][j] == -player: #if there's an enemy piece, threat cannot continue in this direction
        lengthPos = k-1
        blocked = True
        break
    i,j = x,y
    for k in range(1,maxLength):  #crawl direction out to max length    
      i -= direction[0]
      j -= direction[1]
      if i < 0 or i >= len(board) or j < 0 or j >= len(board[0]):
        lengthNeg = k-1
        blocked = True
        break
      if board[i][j] == 0:
        continue
      elif board[i][j] == player:  #if new piece of 
        tilesInARow+=1
      elif board[i][j] == -player: #if there's an enemy piece, threat cannot continue in this direction
        lengthNeg = k-1
        blocked = True
        break
    if lengthNeg !=0 and lengthPos != 0: #if continuous length is bounded on both ends
      maxLengthAlongAxis = lengthNeg + lengthPos + 1
      #if the max length of contiguous spaces containing this point between obstructions can't possibly generate a winning threat
      if maxLengthAlongAxis < 5: 
        break
    if tilesInARow >= 5:  
       return np.inf #if this point is part of a winning threat, return infinity
    if blocked:
      value += lookup[clamp(2*(tilesInARow)-2,0, len(lookup)-1)]  #if the threat is blocked on one side, use the lookup table to get the value of the threat
    else:
      value += lookup[clamp(2*(tilesInARow)-1,0, len(lookup)-1)]
  return value

# def convolved_line_scores(board, player=1):
#     # Player, opponent, and empty masks
#     player_mask = (board == player)*1
#     opponent_mask = (board == -player)*1
#     empty_mask = (board == 0)*1

#     score_map = np.zeros_like(board, dtype=int)

#     for kernel in kernels:
#         # Convolve player presence
#         player_conv = signal.convolve2d(player_mask, kernel, mode='same', boundary='fill', fillvalue=0)
#         # Convolve opponent presence to mask broken lines
#         opponent_conv = signal.convolve2d(opponent_mask, kernel, mode='same', boundary='fill', fillvalue=0)

#         # Score only at empty locations, and only if no opponent pieces block the line
#         valid = (empty_mask == 1) & (opponent_conv == 0)
#         score_map += np.where(valid, player_conv, 0)*1

#     return score_map

# def generate_point_valuations():
#     npBoard = np.array(board, dtype=int)
#     npBoard[npBoard ==2] = -1
#     offensiveScoreMap = convolved_line_scores(npBoard, player=1)    
#     defensiveScoreMap = convolved_line_scores(npBoard, player=-1)
#     lookup = np.array(genome[:-1])
#     offensiveScoreMap = lookup[offensiveScoreMap]
#     defensiveScoreMap = lookup[defensiveScoreMap]
#     # print("Defensive Score Map: ")
#     # for row in defensiveScoreMap:
#     #     print(row)
#     overallPointValues = (genome[-1] * offensiveScoreMap) + (1-genome[-1]) * defensiveScoreMap
#     # print("Overall Points Values: ")
#     # for row in overallPointValues:
#     #     print(row)
#     return overallPointValues

def brain_init():
    if state.width < 5 or state.height < 5:
        pp.pipe_out("ERROR size of the board")
        return
    if state.width > MAX_BOARD or state.height > MAX_BOARD:
        pp.pipe_out("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    pp.pipe_out("OK")


def brain_restart():
    for x in range(state.width):
        for y in range(state.height):
            board[x][y] = 0
    pp.pipe_out("OK")


def is_valid(p: Point):
    return p.x >= 0 and p.y >= 0 and p.x < state.width and p.y < state.height


def is_free(p: Point):
    return is_valid(p) and board[p.x][p.y] == 0


def brain_my(p: Point):
    if is_free(p):
        board[p.x][p.y] = 1
    else:
        pp.pipe_out(f"ERROR my move {p}")


def brain_opponents(p: Point):
    if is_free(p):
        board[p.x][p.y] = 2
    else:
        pp.pipe_out(f"ERROR opponents's move {p}")


def brain_block(p: Point):
    if is_free(p):
        board[p.x][p.y] = 3
    else:
        pp.pipe_out(f"ERROR winning move {p}")


def brain_takeback(p: Point):
    if (is_valid(p) and (board[p.x][p.y] != 0)):
        board[p.x][p.y] = 0
        return 0
    return 2


def brain_turn():
    #if AI slated for termination, return immediately
    if state.terminate_ai:
        return
    npBoard = np.array(board, dtype=int)
    offensiveScores = np.zeros_like(board, dtype=int)
    defensiveScores = np.zeros_like(board, dtype=int)
    totalScores = np.zeros_like(board, dtype=int)
    relevantPositions = identify_relevant_positions(npBoard)
    #Replace Gomocup standard format of 2 = opponent piece for computations
    npBoard[npBoard == 2] = -1
    validPositions = np.zeros_like(board, dtype=int)
    validPositions[npBoard==0] = 1
    for x in range(len(board)):
        for y in range(len(board[0])):
            if relevantPositions[x][y] == 1 and validPositions[x][y]==1:    #only calculate scores for valid points within 5 of another piece
                offensiveScores[x][y] = calculate_value_at_point(npBoard, x, y)
                defensiveScores[x][y] = calculate_value_at_point(npBoard, x, y, player=-1)
                totalScores[x][y] = genome[-1]*offensiveScores[x][y] + (1-genome[-1])*defensiveScores[x][y]
    maxScore = np.max(totalScores)
    minScore = np.min(totalScores)
    if maxScore == minScore:  #if all scores are equal, suggest the center of the board
        pp.suggest(int(state.width // 2), int(state.height // 2))
        return
    else:
        # Find the point with the maximum score
        x, y = np.unravel_index(np.argmax(totalScores), totalScores.shape)
        p = Point(int(x), int(y))
        if not (is_free(p) and is_valid(p)):
            pp.pipe_out(f"ERROR my move {p}")
            return
    
    # i = 0   # number of iterations to find a free point
    # # find a random free point
    # while True:
    #     p = Point(x=random.randint(0, state.width), y=random.randint(0, state.height))  #generate random point
    #     i += 1
    #     if state.terminate_ai:  # check if termination is requested
    #         return
    #     if is_free(p):
    #         break
    # if i > 1:
    #     pp.pipe_out("DEBUG {} coordinates didn't hit an empty field".format(i)) #log how many random coordinates were generated
    pp.do_mymove(p)


def brain_end():
    pass


def brain_about():
    pp.pipe_out(pp.infotext)


# if DEBUG_EVAL:
#     import win32gui

#     def brain_eval(x, y):
#         # TODO check if it works as expected
#         wnd = win32gui.GetForegroundWindow()
#         dc = win32gui.GetDC(wnd)
#         rc = win32gui.GetClientRect(wnd)
#         c = str(board[x][y])
#         win32gui.ExtTextOut(dc, rc[2] - 15, 3, 0, None, c, ())
#         win32gui.ReleaseDC(wnd, dc)


######################################################################
# A possible way how to debug brains.
# To test it, just "uncomment" it (delete enclosing """)
######################################################################
"""
# define a file for logging ...
DEBUG_LOGFILE = "/tmp/pbrain-pyrandom.log"
# ...and clear it initially
with open(DEBUG_LOGFILE,"w") as f:
	pass

# define a function for writing messages to the file
def logDebug(msg):
	with open(DEBUG_LOGFILE,"a") as f:
		f.write(msg+"\n")
		f.flush()

# define a function to get exception traceback
def logTraceBack():
	import traceback
	with open(DEBUG_LOGFILE,"a") as f:
		traceback.print_exc(file=f)
		f.flush()
	raise

# use logDebug wherever
# use try-except (with logTraceBack in except branch) to get exception info
# an example of problematic function
def brain_turn():
	logDebug("some message 1")
	try:
		logDebug("some message 2")
		1. / 0. # some code raising an exception
		logDebug("some message 3") # not logged, as it is after error
	except:
		logTraceBack()
"""
######################################################################

# "overwrites" functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
# pp.brain_eval = brain_eval


def main():
    pp.main()


if __name__ == "__main__":
    main()
