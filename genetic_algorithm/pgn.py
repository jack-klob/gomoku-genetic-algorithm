import chess.pgn
from pydantic import BaseModel


class TournamentResult(BaseModel):
    wins: int = 0
    losses: int = 0
    draws: int = 0


class AgentScore(BaseModel):
    name: str
    score: int


with open("log/results.pgn") as f:
    results: dict[str, TournamentResult] = dict()
    game_count = 0

    while True:
        game_headers = chess.pgn.read_headers(f)

        if not game_headers:
            break

        game_count += 1
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

    scores: list[AgentScore] = []
    for agent, result in results.items():
        result: TournamentResult = result
        score = result.wins * 2 + result.draws
        scores.append(AgentScore(name=agent, score=score))

    print(f"Parsed results for {game_count} games")
    scores.sort(key=lambda s: s.score, reverse=True)
    for i, score in enumerate(scores):
        print(f"{i}. {score.name}: {score.score}")
