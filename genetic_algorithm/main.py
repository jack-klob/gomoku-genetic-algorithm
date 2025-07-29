import json
import os

from agent import GomocupAgent
from population import Population
from tournament import Tournament

POPULATION_SIZE = 50


def main():
    with open("gomocup_agents/agents.json") as f:
        data: list = json.load(f)

    gomocup_agents = [GomocupAgent(**entry) for entry in data]

    pop = Population(POPULATION_SIZE)
    tournament = Tournament()

    print(f"Starting Genetic Algorithm with {POPULATION_SIZE} agents")
    print("Strategy: Top 8 performers crossbreed, keep top 2 elites each generation")
    print("-" * 70)

    # Run genetic algorithm for multiple generations
    while True:
        print(f"\n=== GENERATION {pop.generation} ===")

        # Run tournament to evaluate fitness
        print("Running tournament...")
        tournament.population_trial(pop, gomocup_agents)

        # Calculate fitness values from tournament results
        print("Calculating fitness values...")
        pop.generate_fitness_values(tournament.pgn_path)

        # Show statistics for this generation
        stats = pop.get_statistics()
        print(f"\nGeneration {pop.generation} Results:")
        print(f"  Best fitness: {stats['best']:.2f}")
        print(f"  Average fitness: {stats['average']:.2f}")
        print(f"  Worst fitness: {stats['worst']:.2f}")

        # Show top 5 agents
        top_agents = pop.get_top_agents(5)
        print("\nTop 5 agents:")
        for i, agent in enumerate(top_agents):
            print(f"  {i}. {agent.name}: {agent.fitness:.2f}")

        # Log to generation file
        with open("./log/generation_results.txt", "a") as f:
            print(
                f"Generation {pop.generation} {top_agents[0].name}: {stats['best']}",
                file=f,
            )

        # Save final population to file
        gen_dir = "./log/generations"
        os.makedirs(gen_dir, exist_ok=True)
        with open(f"{gen_dir}/final_population_gen{pop.generation}.json", "w") as f:
            json.dump([agent.model_dump() for agent in pop.agents], f, indent=4)

        print(f"\nEvolving to generation {pop.generation + 1}...")
        pop.evolve()


if __name__ == "__main__":
    main()
