import json

from agent import GomocupAgent
from population import Population
from tournament import Tournament

POPULATION_SIZE = 25


def main():
    with open("gomocup_agents/agents.json") as f:
        data: list = json.load(f)

    gomocup_agents = [GomocupAgent(**entry) for entry in data]

    pop = Population(50)
    tournament = Tournament()
    # tournament.population_trial(pop, gomocup_agents)
    tournament.split_tournament(pop)
    pop.generate_fitness_values(tournament.pgn_path)


if __name__ == "__main__":
    main()
