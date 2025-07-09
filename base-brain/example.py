import random

import pisqpipe as pp
from pisqpipe import state
from structs import Point

pp.infotext = (
    'name="pbrain-genetic", authors="Andrew Petten, Chance Kane, Jack Klobchar, Tim Xu"'
)


MAX_BOARD = 100
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]


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
        pp.pipe_out("ERROR Maximal board size is {}".format(MAX_BOARD))
        return

    brain_restart()


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
    if (
        p.x >= 0
        and p.y >= 0
        and p.x < state.width
        and p.y < state.height
        and board[p.x][p.y] != 0
    ):
        board[p.x][p.y] = 0
        return 0
    return 2


def brain_turn():
    if state.terminate_ai:
        return

    rows_idx = [n for n in range(state.height)]
    col_idx = [n for n in range(state.width)]

    random.shuffle(rows_idx)
    for row in rows_idx:
        random.shuffle(col_idx)

        for x in col_idx:
            p = Point(x=x, y=row)
            if is_free(p):
                pp.do_mymove(p)
                return

        if state.terminate_ai:
            return


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
