import random

from agent import GeneticAgent


def crossover(parent1: GeneticAgent, parent2: GeneticAgent) -> GeneticAgent:
    # Placeholder for crossover
    return parent1


class Population:
    def __init__(self, size):
        self.agents = [
            GeneticAgent(name=f"Agent {i}", cmd="../base_brain/dist/pbrain-testexe.exe")
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
