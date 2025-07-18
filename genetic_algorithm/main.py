import json
import subprocess

from agent import GomocupAgent
from population import Population

POPULATION_SIZE = 100
GOMOKU_CLI_PATH = "c-gomoku-cli.exe"
AGENT_FOLDER_PATH = "./gomocup_agents/"


class Tournament:
    def __init__(self):
        self.time_per_turn = 5
        self.time_per_game = 180
        self.total_games = 5
        self.concurrency = 32
        self.turns_until_draw = 200

    def _pre_engine_params(self) -> list[str]:
        return ["-each", f"tc={self.time_per_game}/{self.time_per_turn}"]

    def _post_engine_params(self) -> list[str]:
        return [
            "-boardsize",
            "20",
            "-concurrency",
            f"{self.concurrency}",
            "-drawafter",
            f"{self.turns_until_draw}",
            "-games",
            f"{self.total_games}",
        ]

    @staticmethod
    def _gomocup_agent_to_params(agent: GomocupAgent):
        return [
            "-engine",
            f"name={agent.name}",
            f'cmd="{AGENT_FOLDER_PATH}{agent.path}"',
        ]

    def round_robin(self, genetic_population: Population):
        pass

    def gauntlet(self, gomocup_agents: list[GomocupAgent]):
        # For testing just make the first gomocup agent the main agent
        # This method should really take a genetic agent as well to be the main agent

        command: list[str] = [GOMOKU_CLI_PATH]
        command += self._pre_engine_params()
        for agent in gomocup_agents:
            command += self._gomocup_agent_to_params(agent)
        command += self._post_engine_params()
        command.append("-gauntlet")
        command += ["-sgf", "./sgf_file"]

        subprocess.run(command)

        print(" ".join(command))

        pass


def main():
    with open("gomocup_agents/agents.json") as f:
        data: list = json.load(f)

    agents = [GomocupAgent(**entry) for entry in data]

    tournament_manager = Tournament()
    tournament_manager.gauntlet(agents)


if __name__ == "__main__":
    main()
