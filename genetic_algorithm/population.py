import random

import chess.pgn
from agent import GeneticAgent


def crossover(parent1: GeneticAgent, parent2: GeneticAgent) -> GeneticAgent:
    """
    Create a child agent by combining weights from two parents using uniform crossover
    """
    child_weights = []
    for i in range(len(parent1.weights)):
        # Randomly choose weight from either parent
        if random.random() < 0.5:
            child_weights.append(parent1.weights[i])
        else:
            child_weights.append(parent2.weights[i])

    # Create child with unique name for new generation
    child = GeneticAgent(
        name="child",
        cmd=parent1.cmd,  # Use same command as parents
        weights=child_weights,
    )
    return child


class Population:
    def __init__(self, size):
        self.generation = 1
        self.agents = [
            GeneticAgent(
                name=f"Agent {self.generation}.{i}",
                cmd="../base_brain/dist/pbrain-agent/pbrain-agent.exe",
            )
            for i in range(size)
        ]

    def get_top_agents(self, n: int):
        """Get the top n agents by fitness"""
        self.agents.sort(key=lambda agent: agent.fitness, reverse=True)
        return self.agents[:n]

    def evolve(self):
        """
        Evolve the population:
        - Take top 8 performing agents
        - Cross breed them for offspring
        - Apply slight mutation
        - Keep top 2 agents from previous generation as elites
        """
        # Sort agents by their fitness (descending order)
        self.agents.sort(key=lambda agent: agent.fitness, reverse=True)

        # Get top 8 performers for crossbreeding
        top_performers = self.agents[:8]

        # Keep top 2 as elites (unchanged)
        elites = self.agents[:2].copy()
        print(
            f"Keeping elites: {elites[0].name} (fitness: {elites[0].fitness:.2f}), {elites[1].name} (fitness: {elites[1].fitness:.2f})"
        )

        # Increment generation
        self.generation += 1

        # Update elite names for new generation - preserve original number but add ELITE tag
        for elite in elites:
            if "(ELITE)" not in elite.name:
                elite.name = f"{elite.name} (ELITE)"
            elite.fitness = -1  # Reset fitness for new tournament

        # Create new population starting with elites
        new_agents = elites.copy()

        # Fill the rest of the population with offspring from top 8 performers
        offspring_count = len(self.agents) - 2  # Total minus the 2 elites

        for _ in range(offspring_count):
            # Select two random parents from top 8 performers
            parent1 = random.choice(top_performers)
            parent2 = random.choice(top_performers)

            # Create child through crossover
            child = crossover(parent1, parent2)

            # Give child proper name for new generation
            child.name = f"Agent {self.generation}.{len(new_agents)}"
            child.fitness = -1  # Reset fitness for new tournament

            # Apply mutation with slight probability
            child.mutate()

            new_agents.append(child)

        # Update population
        self.agents = new_agents

        print(f"Evolution complete. Generation: {self.generation}")
        print(
            f"Population size: {len(self.agents)} (2 elites + {offspring_count} offspring)"
        )
        print("Offspring created from top 8 performers with crossover and mutation")

    def get_statistics(self):
        """Get population statistics"""

        fitnesses = [agent.fitness for agent in self.agents if agent.fitness != -1]
        if not fitnesses:
            return {"best": 0, "average": 0, "worst": 0}

        return {
            "best": max(fitnesses),
            "average": sum(fitnesses) / len(fitnesses),
            "worst": min(fitnesses),
        }

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
                if agent.name not in results:
                    continue
                agent.fitness = round(results[agent.name], 4)
                print(f"{agent.name}: fitness = {agent.fitness}")
