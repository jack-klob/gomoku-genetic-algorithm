# functions and variables for pipe AI and functions that communicate with manager through pipes

import sys
from typing import Optional

import win32api
import win32event
import win32process
import win32security
from structs import GameParameters, Point

DEBUG = False
ABOUT_FUNC = True
DEBUG_EVAL = False

state = GameParameters()
event1 = win32event.CreateEvent(None, 0, 0, None)
event2 = win32event.CreateEvent(None, 1, 1, None)


# you have to implement these functions
def brain_init():
    """create the board and call pipeOut("OK") or pipeOut("ERROR Maximal board size is ..")"""
    raise NotImplementedError


def brain_restart():
    """delete old board, create new board, call pipeOut("OK")"""
    raise NotImplementedError


def brain_turn():
    """choose your move and call do_mymove(x,y), 0 <= x < width, 0 <= y < height"""
    raise NotImplementedError


def brain_my(p: Point):
    """put your move to the board"""
    raise NotImplementedError


def brain_opponents(p: Point):
    """put opponent's move to the board"""
    raise NotImplementedError


def brain_block(p: Point):
    """square [x,y] belongs to a winning line (when info_continuous is 1)"""
    raise NotImplementedError


def brain_takeback(p: Point):
    """clear one square, return value: 0: success, 1: not supported, 2: error"""
    raise NotImplementedError


def brain_end():
    """delete temporary files, free resources"""
    raise NotImplementedError


def brain_eval(p: Point):
    """display evaluation of square [x,y]"""
    raise NotImplementedError


"""AI identification (copyright, version)"""
infotext = ""


def brain_about():
    """call pipeOut(" your AI info ")"""
    raise NotImplementedError


def pipe_out(what):
    """write a line to sys.stdout"""
    print(what)
    sys.stdout.flush()


def do_mymove(p: Point):
    brain_my(p)
    pipe_out(p)


def suggest(x, y):
    """send suggest"""
    pipe_out("SUGGEST {},{}".format(x, y))


def get_line():
    """read a line from sys.stdin"""
    return sys.stdin.readline().strip()


def parse_coord(param) -> Optional[Point]:
    """parse coordinates x,y"""
    if param.count(",") != 1:
        return None

    x, _, y = param.partition(",")
    x, y = [int(v) for v in (x, y)]

    if x < 0 or y < 0 or x >= state.width or y >= state.height:
        return None

    return Point(x=x, y=y)


def parse_3int_chk(param) -> Optional[tuple[Point, int]]:
    """parse coordinates x,y and player number z"""
    if param.count(",") != 2:
        return None
    x, y, z = param.split(",")
    x, y, z = [int(v) for v in (x, y, z)]

    return (Point(x, y), z)


def get_cmd_param(command: str, input: str):
    """return word after command if input starts with command, otherwise return None"""
    cl = command.lower()
    il = input.lower()
    n1 = len(command)
    n2 = len(input)
    if n1 > n2 or not il.startswith(cl):
        return None  # it is not command
    return input[n1:].lstrip()


def thread_loop():
    """main function for the working thread"""
    while True:
        win32event.WaitForSingleObject(event1, win32event.INFINITE)
        brain_turn()
        win32event.SetEvent(event2)


def turn():
    """start thinking"""
    state.terminate_ai = False
    win32event.ResetEvent(event2)
    win32event.SetEvent(event1)


def stop():
    """stop thinking"""
    state.terminate_ai = True
    win32event.WaitForSingleObject(event2, win32event.INFINITE)


def start():
    state.start_time = win32api.GetTickCount()
    stop()
    if not state.width:
        state.width = state.height = 20
        brain_init()


def do_command(cmd):
    """do command cmd"""
    #
    param = get_cmd_param("info", cmd)
    if param is not None:
        info = get_cmd_param("max_memory", param)
        if info is not None:
            state.info_max_memory = int(info)
            return
        #
        info = get_cmd_param("timeout_match", param)
        if info is not None:
            state.info_timeout_match = int(info)
            return
        #
        info = get_cmd_param("timeout_turn", param)
        if info is not None:
            state.info_timeout_turn = int(info)
            return
        #
        info = get_cmd_param("time_left", param)
        if info is not None:
            state.info_time_left = int(info)
            return
        #
        info = get_cmd_param("game_type", param)
        if info is not None:
            state.info_game_type = int(info)
            return
        #
        info = get_cmd_param("rule", param)
        if info is not None:
            e = int(info)
            state.info_exact5 = e & 1
            state.info_continuous = (e >> 1) & 1
            state.info_renju = (e >> 2) & 1
            return
        #
        info = get_cmd_param("folder", param)
        if info is not None:
            state.dataFolder = info
            return
        #
        info = get_cmd_param("evaluate", param)
        if DEBUG_EVAL and info is not None:
            p: Optional[Point] = parse_coord(info)
            if p is not None:
                brain_eval(p)
            return
        # unknown info is ignored
        return
    #
    param = get_cmd_param("start", cmd)
    if param is not None:
        dimension = int(param)
        if dimension < 5:
            state.width = state.height = 0
            pipe_out("ERROR bad START parameter")
        else:
            state.width = state.height = dimension
            start()
            brain_init()
        return
    #
    param = get_cmd_param("rectstart", cmd)
    if param is not None:
        if param.count(",") != 1:
            state.width = state.height = 0
        else:
            start_width, _, start_height = param.partition(",")
            start_width = int(start_width)
            start_height = int(start_height)

            if start_width < 5 or start_height < 5:
                state.width = state.height = 0
                pipe_out("ERROR bad RECTSTART parameters")
            else:
                start()
            brain_init()
        return
    #
    param = get_cmd_param("restart", cmd)
    if param is not None:
        start()
        brain_restart()
        return
    #
    param = get_cmd_param("turn", cmd)
    if param is not None:
        start()
        p: Optional[Point] = parse_coord(param)
        if p is None:
            pipe_out("ERROR bad coordinates")
        else:
            brain_opponents(p)
            turn()
        return
    #
    param = get_cmd_param("play", cmd)
    if param is not None:
        start()
        p: Optional[Point] = parse_coord(param)
        if p is None:
            pipe_out("ERROR bad coordinates")
        else:
            do_mymove(p)
        return
    #
    param = get_cmd_param("begin", cmd)
    if param is not None:
        start()
        turn()
        return
    #
    param = get_cmd_param("about", cmd)
    if param is not None:
        if ABOUT_FUNC:
            brain_about()
        else:
            pipe_out(infotext)
        return
    #
    param = get_cmd_param("end", cmd)
    if param is not None:
        stop()
        brain_end()
        sys.exit(0)
        return
    #
    param = get_cmd_param("board", cmd)
    if param is not None:
        start()
        while True:  # fill the whole board
            cmd = get_line()
            res = parse_3int_chk(cmd)
            if res is not None:
                p, who = res
                if who == 1:
                    brain_my(p)
                elif who == 2:
                    brain_opponents(p)
                elif who == 3:
                    brain_block(p)
            else:
                if cmd.lower() != "done":
                    pipe_out("ERROR x,y,who or DONE expected after BOARD")
                break
        turn()
        return
    #
    param = get_cmd_param("takeback", cmd)
    if param is not None:
        start()
        t = "ERROR bad coordinates"
        p: Optional[Point] = parse_coord(param)
        if p is not None:
            e = brain_takeback(p)
            if e == 0:
                t = "OK"
            elif e == 1:
                t = "UNKNOWN"
        pipe_out(t)
        return
    #
    pipe_out("UNKNOWN command {}".format(cmd))


def main():
    """main function for AI console application"""

    sa = win32security.SECURITY_ATTRIBUTES()
    win32process.beginthreadex(sa, 0, thread_loop, (), 0)

    while True:
        cmd = get_line()
        do_command(cmd)
