import random

from agent import Agent


def crossover(parent1: Agent, parent2: Agent) -> Agent:
    # Placeholder for crossover
    return parent1


class Population:
    def __init__(self, size):
        self.agents = [Agent(name=f"Agent {i}") for i in range(size)]

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
