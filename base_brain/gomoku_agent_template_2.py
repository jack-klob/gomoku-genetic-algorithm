import json
import sys

import numpy as np
import pisqpipe as pp
from pisqpipe import state
from scipy import signal
from structs import Point

pp.infotext = 'name="pbrain-geneticPeabrain-lookahead", authors="Andrew Petten, Chance Kane, Jack Klobchar, Tim Xu"'
# genome for the genetic algorithm: 11 values, 10 arbitrary, one constrained to [0,1]
# genome = [one-closed,one-open,two-closed,two-open,three-closed,three-open,four-closed,four-open, aggression]
# default genome values
genome = [0.004, 0.008, 0.016, 0.032, 0.064, 0.56, 0.5, 1.0, 0.5]
THREAT_SCALE = 1000

MAX_BOARD = 20
# 0 = empty, 1 = my stone, 2 = opponent's stone, 3 = winning move
board = [[0 for _ in range(MAX_BOARD)] for _ in range(MAX_BOARD)]
relevanceKernal = np.ones((9, 9))  # used to track relevance of a point
directions = [[0, 1], [1, 1], [1, 0], [1, -1]]


def clamp(value, min_val, max_val):
    """Clamps a single numerical value within a specified range."""
    return max(min(value, max_val), min_val)


# Generate and return a board mask indicating which positions are within relevance range of another piece
def identify_relevant_positions(board):
    relevantMask = np.zeros_like(board, dtype=int)
    convolved = signal.convolve2d(
        board, relevanceKernal, mode="same", boundary="fill", fillvalue=0
    )
    relevantMask = (convolved != 0).astype(int)
    return relevantMask


# Evaluate raw threat value at a point for a given player
def calculate_value_at_point(board, x, y, maxLength=5, player=1):
    value = 0
    lookup = np.array(genome[:-1]) * THREAT_SCALE
    for direction in directions:
        i, j = x, y
        tilesInARow = 1
        lengthPos, lengthNeg = 0, 0
        blocked = False

        # forward direction
        for k in range(1, maxLength):
            i += direction[0]
            j += direction[1]
            if i < 0 or i >= board.shape[0] or j < 0 or j >= board.shape[1]:
                lengthPos = k - 1
                blocked = True
                break
            if board[i][j] == 0:
                continue
            elif board[i][j] == player:
                tilesInARow += 1
            elif board[i][j] == -player:
                lengthPos = k - 1
                blocked = True
                break
        # backward direction
        i, j = x, y
        for k in range(1, maxLength):
            i -= direction[0]
            j -= direction[1]
            if i < 0 or i >= board.shape[0] or j < 0 or j >= board.shape[1]:
                lengthNeg = k - 1
                blocked = True
                break
            if board[i][j] == 0:
                continue
            elif board[i][j] == player:
                tilesInARow += 1
            elif board[i][j] == -player:
                lengthNeg = k - 1
                blocked = True
                break

        # if bounded both ends and too short, skip
        if lengthNeg != 0 and lengthPos != 0:
            if (lengthNeg + lengthPos + 1) < 5:
                break
        # winning
        if tilesInARow >= 5:
            return 2.0 * THREAT_SCALE

        # add value based on blocked vs open
        if blocked:
            idx = clamp(2 * tilesInARow - 2, 0, len(lookup) - 1)
        else:
            idx = clamp(2 * tilesInARow - 1, 0, len(lookup) - 1)
        value += lookup[idx]
    return value


def evaluate_with_lookahead(npBoard, x, y):
    """
    Return a lookahead score for placing at (x,y):
      aggression * our_immediate_value  -  (1-aggression) * opponent_best_response
    """
    aggression = genome[-1]

    # 1) our immediate threat
    our_val = calculate_value_at_point(npBoard, x, y, player=1)

    # 2) simulate move
    board2 = npBoard.copy()
    board2[x, y] = 1

    # 3) compute opponent's best reply
    rel2 = identify_relevant_positions(board2)
    best_opp = 0.0
    for i in range(board2.shape[0]):
        for j in range(board2.shape[1]):
            if rel2[i, j] and board2[i, j] == 0:
                opp_val = calculate_value_at_point(board2, i, j, player=-1)
                if opp_val > best_opp:
                    best_opp = opp_val

    # 4) weighted difference
    return aggression * our_val - (1 - aggression) * best_opp


def brain_restart():
    for x in range(state.width):
        for y in range(state.height):
            board[x][y] = 0
    pp.pipe_out("OK")


def brain_init():
    if state.width < 5 or state.height < 5:
        pp.pipe_out("ERROR size of the board")
        return
    if state.width > MAX_BOARD or state.height > MAX_BOARD:
        pp.pipe_out(f"ERROR Maximal board size is {MAX_BOARD}")
        return
    brain_restart()


def is_valid(p: Point):
    return 0 <= p.x < state.width and 0 <= p.y < state.height


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
    if is_valid(p) and board[p.x][p.y] != 0:
        board[p.x][p.y] = 0
        return 0
    return 2


def brain_turn():
    # early exit if terminated
    if state.terminate_ai:
        return

    # snapshot and identify relevance
    npBoard = np.array(board, dtype=int)
    relevant = identify_relevant_positions(npBoard)

    # convert opponent pieces to -1 for threat eval
    npBoard[npBoard == 2] = -1
    valid = (npBoard == 0)

    # score every relevant, empty cell with one-ply lookahead
    scores = np.full_like(npBoard, -np.inf, dtype=float)
    for x in range(state.width):
        for y in range(state.height):
            if state.terminate_ai:
                return
            if relevant[x, y] and valid[x, y]:
                scores[x, y] = evaluate_with_lookahead(npBoard, x, y)

    # choose best move
    max_score = np.max(scores)
    if max_score == -np.inf:
        p = Point(state.width // 2, state.height // 2)
        pp.pipe_out("DEBUG no lookahead positions, choosing center...")
    else:
        choices = np.argwhere(scores == max_score)
        x, y = choices[np.random.choice(len(choices))]
        p = Point(int(x), int(y))

    if not is_free(p):
        pp.pipe_out(f"ERROR my move {p}")
        return
    pp.do_mymove(p)


def brain_end():
    pass


def brain_about():
    pp.pipe_out(pp.infotext)

# hook into pisqpipe
pp.brain_init      = brain_init
pp.brain_restart   = brain_restart
pp.brain_my        = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block     = brain_block
pp.brain_takeback  = brain_takeback
pp.brain_turn      = brain_turn
pp.brain_end       = brain_end
pp.brain_about     = brain_about


def load_genome():
    if len(sys.argv) <= 1:
        pp.pipe_out("DEBUG no genome file provided, using default genome.")
        return

    data = json.loads(sys.argv[1])
    global genome
    if isinstance(data, list) and len(data) == len(genome) and all(0 <= v <= 1 for v in data):
        genome = data
        pp.pipe_out(f"DEBUG using genome: {genome}")
    else:
        raise ValueError(
            f"Genome must be list of length {len(genome)} with values between 0 and 1."
        )


def main():
    load_genome()
    pp.main()

if __name__ == "__main__":
    main()
