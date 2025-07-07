from typing import NamedTuple


class Point(NamedTuple):
    x: int
    y: int

    def __str__(self):
        return f"{self.x},{self.y}"


class GameParameters:
    def __init__(self):
        # information about a game - you should use these variables
        """the board size"""
        self.width: int = 0
        self.height: int = 0

        """time for one turn in milliseconds"""
        self.info_timeout_turn: int = 30000
        """total time for a game"""
        self.info_timeout_match: int = 1000000000
        """left time for a game"""
        self.info_time_left: int = 1000000000
        """maximum memory in bytes, zero if unlimited"""
        self.info_max_memory: int = 0
        """0: human opponent, 1: AI opponent, 2: tournament, 3: network tournament"""
        self.info_game_type: int = 1
        """0: five or more stones win, 1: exactly five stones win"""
        self.info_exact5: int = 0
        """0: gomoku, 1: renju"""
        self.info_renju: int = 0
        """0: single game, 1: continuous"""
        self.info_continuous: int = 0
        """return from brain_turn when terminate_ai > 0"""
        self.terminate_ai: bool = False
        """tick count at the beginning of turn"""
        self.start_time: int = 0
        """folder for persistent files"""
        self.dataFolder: str = ""
