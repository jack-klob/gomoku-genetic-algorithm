import os
import random
import subprocess
import time
from typing import Sequence

from agent import Agent, GeneticAgent, GomocupAgent
from population import Population

GOMOKU_CLI_PATH = "c-gomoku-cli.exe"
AGENT_FOLDER_PATH = "./gomocup_agents/"


def _agent_to_params(agent: Agent):
    if isinstance(agent, GomocupAgent):
        return [
            "-engine",
            f"name={agent.name}",
            f'cmd="{AGENT_FOLDER_PATH}{agent.cmd}"',
        ]
    elif isinstance(agent, GeneticAgent):
        return [
            "-engine",
            f"name={agent.name}",
            f'cmd={agent.cmd} "{agent.weights}"',
        ]
    else:
        raise ValueError("Unknown agent type")


class Tournament:
    def __init__(self):
        self.time_per_turn = 5
        self.time_per_game = 180
        self.games_per_pair = 2
        self.concurrency = 16
        self.pgn_path = "./log/results.pgn"

    def _new_pgn_file(self, name: str):
        self.pgn_path = name
        if os.path.exists(self.pgn_path):
            os.remove(self.pgn_path)

    def _pre_engine_params(self) -> list[str]:
        return [
            "-each",
            f"tc={self.time_per_game}/{self.time_per_turn}",
            "tolerance=20",
        ]

    def _post_engine_params(self) -> list[str]:
        # delete results.pgn file since cli program will append
        return [
            "-boardsize",
            "20",
            "-concurrency",
            f"{self.concurrency}",
            "-games",
            f"{self.games_per_pair}",
            "-pgn",
            self.pgn_path,
        ]

    def round_robin(self, agents: Sequence[Agent]):
        command: list[str] = [GOMOKU_CLI_PATH]
        command += self._pre_engine_params()

        for agent in agents:
            command += _agent_to_params(agent)

        command += self._post_engine_params()
        result = subprocess.run(command, stdout=subprocess.DEVNULL)

        result.check_returncode()

    def gauntlet(self, main_agent: Agent, population: Sequence[Agent]):
        command: list[str] = [GOMOKU_CLI_PATH]
        command += self._pre_engine_params()

        command += _agent_to_params(main_agent)
        for agent in population:
            command += _agent_to_params(agent)

        command += self._post_engine_params()
        command.append("-gauntlet")

        result = subprocess.run(command, stdout=subprocess.DEVNULL)
        result.check_returncode()

    def split_random_groups(self, agents: Sequence, group_size=10, repeats=1):
        mut_agents = list(agents)

        groups = []

        for _ in range(repeats):
            random.shuffle(mut_agents)
            groups += [
                mut_agents[i : i + group_size]
                for i in range(0, len(agents), group_size)
            ]
        return groups

    def population_trial(
        self, population: Population, gomocup_agents: list[GomocupAgent]
    ):
        """run a tournament where each genetic agents plays each gomocup agent some number of times"""

        self._new_pgn_file("./log/population_trial.pgn")

        for i, gomocup_agent in enumerate(gomocup_agents):
            start = time.time()
            print(f"Gauntlet {i + 1}/{len(gomocup_agents)} vs {gomocup_agent.name}")
            self.gauntlet(gomocup_agent, population.agents)
            print(f"completed in {round(time.time() - start, 2)}")

    def split_tournament(self, population: Population):
        """run several mini round robin tournaments within the population"""

        self._new_pgn_file(f"./log/population_tournament{population.generation}.pgn")
        self.games_per_pair = 2

        agents_groupings = self.split_random_groups(population.agents, repeats=1)

        # Run many round robin tournaments for each member of the population
        with open("./log/tournamentlog.txt", "w") as f:
            for i, group in enumerate(agents_groupings):
                print(f"generation {population.generation}", file=f, flush=True)
                agent_names = [agent.name for agent in group]
                print(
                    f"Round robin tournament for group {i + 1}/{len(agents_groupings)}: {agent_names}",
                    file=f,
                    flush=True,
                )

                start = time.time()
                self.round_robin(group)
                print(
                    f"tournament finished in {round(time.time() - start, 2)} seconds",
                    file=f,
                    flush=True,
                )
