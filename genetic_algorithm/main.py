import json

from agent import GomocupAgent
from population import Population
from tournament import Tournament

POPULATION_SIZE = 50
GENERATIONS = 10  # Number of generations to run


def main():
    with open("gomocup_agents/agents.json") as f:
        data: list = json.load(f)

    gomocup_agents = [GomocupAgent(**entry) for entry in data]

    pop = Population(POPULATION_SIZE)
    tournament = Tournament()
    
    print(f"Starting Genetic Algorithm with {POPULATION_SIZE} agents for {GENERATIONS} generations")
    print("Strategy: Top 8 performers crossbreed, keep top 2 elites each generation")
    print("-" * 70)
    
    # Run genetic algorithm for multiple generations
    for generation in range(GENERATIONS):
        print(f"\n=== GENERATION {pop.generation} ===")
        
        # Run tournament to evaluate fitness
        print("Running tournament...")
        tournament.split_tournament(pop)
        
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
        print(f"\nTop 5 agents:")
        for i, agent in enumerate(top_agents, 1):
            print(f"  {i}. {agent.name}: {agent.fitness:.2f}")

    
        
        # Evolve to next generation (except for the last generation)
        if generation < GENERATIONS - 1:
            print(f"\nEvolving to generation {pop.generation + 1}...")
            pop.evolve()
        # Run best agent against gauntlet against the Gomokup agents
        print("\nRunning final gauntlet with best agent against Gomocup agents...") 
        best_agent = top_agents[0] 
        test_population = Population(1)
        test_population.agents = [best_agent]
        tournament.pgn_path = f"./log/gomocup_gauntlet{pop.generation}.pgn"
        tournament.games_per_pair = 6
        tournament.gauntlet(best_agent, gomocup_agents)
        # Read .pgn file and get fitness value of best agent
        test_population.generate_fitness_values(tournament.pgn_path)
        print(f"Best agent after gauntlet: {test_population.agents[0].name} with fitness {test_population.agents[0].fitness:.2f}")

        # Save final population to file
        with open(f"./log/final_population_gen{pop.generation}.json", "w") as f:
            json.dump([agent.model_dump() for agent in pop.agents], f, indent=4)

    print(f"\n=== GENETIC ALGORITHM COMPLETE ===")
    print(f"Final generation: {pop.generation}")
    
    # Show final results
    final_stats = pop.get_statistics()
    print(f"\nFinal Statistics:")
    print(f"  Best fitness: {final_stats['best']:.2f}")
    print(f"  Average fitness: {final_stats['average']:.2f}")
    print(f"  Worst fitness: {final_stats['worst']:.2f}")
    
    # Show final top 8 agents (the breeding pool)
    final_top = pop.get_top_agents(8)
    print(f"\nFinal Top 8 agents (breeding pool):")
    for i, agent in enumerate(final_top, 1):
        print(f"  {i}. {agent.name}: {agent.fitness:.2f}")

        


if __name__ == "__main__":
    main()
