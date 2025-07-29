import random

import chess.pgn
from agent import GeneticAgent


def crossover(parent1: GeneticAgent, parent2: GeneticAgent) -> GeneticAgent:
    # Placeholder for crossover
    return parent1


class Population:
    def __init__(self, size):
        self.generation = 1
        self.agents = [
            GeneticAgent(
                name=f"Agent {self.generation}.{i}",
                cmd="../base_brain/dist/pbrain-agent/pbrain-genetic.exe",
            )
            for i in range(size)
        ]

    def evolve(self):
        # Sort agents by their fitness
        self.agents.sort(key=lambda agent: agent.fitness, reverse=True)

        # Select the top half to reproduce
        selected = self.agents[: len(self.agents) // 2]

        # Create new population with crossover and mutation
        new_agents = []
        for _ in range(len(self.agents)):
            parent1 = random.choice(selected)
            parent2 = random.choice(selected)

            child = crossover(parent1, parent2)
            child.mutate()
            new_agents.append(child)

        self.agents = new_agents

    def generate_fitness_values(self, pgn_path: str):
        results: dict[str, float] = {}

        with open(pgn_path, "r") as f:
            game_count = 0

            while True:
                game_headers = chess.pgn.read_headers(f)

                if not game_headers:
                    break

                game_count += 1
                white_agent = game_headers["White"]
                black_agent = game_headers["Black"]
                results.setdefault(white_agent, 0)
                results.setdefault(black_agent, 0)

                def update_entry(key: str, score: str, turns: int):
                    if score == "1":
                        results[key] += 2
                    elif score == "1/2":
                        results[key] += 1
                    elif score == "0":
                        # if its a loss, give small amount of fitness for turns survived
                        turns_for_draw = 400
                        max_points = 0.7
                        results[key] += (turns / (turns_for_draw - 1)) * max_points

                    else:
                        raise ValueError(f"unknown score ({score})")

                white_score, black_score = game_headers["Result"].split("-")
                turns = int(game_headers["PlyCount"])

                update_entry(white_agent, white_score, turns)
                update_entry(black_agent, black_score, turns)

            for agent in self.agents:
                agent.fitness = results[agent.name]
                print(f"{agent.name}: fitness = {agent.fitness}")
