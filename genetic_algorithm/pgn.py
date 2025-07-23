import chess.pgn
from pydantic import BaseModel


class TournamentResult(BaseModel):
    wins: int = 0
    losses: int = 0
    draws: int = 0


with open("log/results.pgn") as f:
    results: dict[str, TournamentResult] = dict()

    while True:
        game_headers = chess.pgn.read_headers(f)

        if not game_headers:
            break

        white = results.setdefault(game_headers["White"], TournamentResult())
        black = results.setdefault(game_headers["Black"], TournamentResult())

        def update_entry(entry: TournamentResult, score: str):
            if score == "1":
                entry.wins += 1
            elif score == "0":
                entry.losses += 1
            elif score == "1/2":
                entry.draws += 1
            else:
                raise ValueError(f"unknown score ({score})")

        white_score, black_score = game_headers["Result"].split("-")
        update_entry(white, white_score)
        update_entry(black, black_score)

    print(results)
