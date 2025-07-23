import subprocess

from agent import GeneticAgent, GomocupAgent
from population import Population

POPULATION_SIZE = 100
GOMOKU_CLI_PATH = "c-gomoku-cli.exe"
AGENT_FOLDER_PATH = "./gomocup_agents/"


class Tournament:
    def __init__(self):
        self.time_per_turn = 5
        self.time_per_game = 180
        self.total_games = 2
        self.concurrency = 32
        self.turns_until_draw = 200

    def _pre_engine_params(self) -> list[str]:
        return ["-each", f"tc={self.time_per_game}/{self.time_per_turn}"]

    def _post_engine_params(self) -> list[str]:
        # delete results.pgn file since cli program will append
        pgn_path = "./log/results.pgn"
        # if os.path.exists(pgn_path):
        #     os.remove(pgn_path)

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
            f'cmd="{AGENT_FOLDER_PATH}{agent.cmd}"',
        ]

    @staticmethod
    def _genetic_agent_to_params(agent: GeneticAgent):
        return ["-engine", f"name={agent.name}", f'cmd="{agent.cmd}"']

    def round_robin(self, genetic_population: Population):
        command: list[str] = [GOMOKU_CLI_PATH]
        command += self._pre_engine_params()

        for agent in genetic_population.agents:
            command += self._genetic_agent_to_params(agent)

        command += self._post_engine_params()

        subprocess.run(command)

    def gauntlet(self, genetic_agent: GeneticAgent, gomocup_agents: list[GomocupAgent]):
        # For testing just make the first gomocup agent the main agent
        # This method should really take a genetic agent as well to be the main agent

        command: list[str] = [GOMOKU_CLI_PATH]
        command += self._pre_engine_params()

        command += self._genetic_agent_to_params(genetic_agent)
        for gomocup_agent in gomocup_agents:
            command += self._gomocup_agent_to_params(gomocup_agent)

        command += self._post_engine_params()
        command.append("-gauntlet")

        subprocess.run(command)


def main():
    # with open("gomocup_agents/agents.json") as f:
    #     data: list = json.load(f)

    # agents = [GomocupAgent(**entry) for entry in data]

    # dummy_genetic = GeneticAgent(
    #     name="random", cmd="../base_brain/dist/pbrain-testexe.exe"
    # )

    population = Population(POPULATION_SIZE)

    tournament_manager = Tournament()
    tournament_manager.round_robin(population)


if __name__ == "__main__":
    main()
