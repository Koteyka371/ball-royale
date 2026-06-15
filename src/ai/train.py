"""
Ball Royale — Neural Network Training Script
Uses Genetic Algorithm to evolve the 'neural' ball type over multiple generations.
"""

import sys
import os
import argparse
import random
import copy
from typing import List

# Ensure we can import from src and tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import simulation engine and AI
from tests.simulate_battle import BattleSimulation
import tests.simulate_battle as sim
from src.ai.neural_network import NeuralNetwork

# Add the 'neural' ball type for simulation dynamically
NEURAL_PROPERTIES = {
    "hp": 100, "speed": 2.5, "damage": 12, "radius": 10,
    "perception_radius": 250, "aggression": 0.5, "color": "cyan",
    "skill": "dash", "skill_cooldown": 4.0
}
sim.BALL_TYPES["neural"] = NEURAL_PROPERTIES

class Agent:
    def __init__(self, nn: NeuralNetwork):
        self.nn = nn
        self.fitness = 0.0

def evaluate_population(population: List[Agent], ticks: int):
    """Run a battle simulation with the population to evaluate fitness."""
    # Ensure there's a mix of neural and standard balls for evaluation
    num_neural = len(population)
    num_standard = num_neural // 2

    sim_instance = BattleSimulation(num_balls=num_neural + num_standard, max_ticks=ticks, arena_size=2000.0)

    # Force the first N balls to be 'neural' and inject their unique NN weights
    neural_balls = []
    for i in range(num_neural):
        ball = sim_instance.balls[i]
        ball.ball_type = "neural"
        # Reset properties from the dynamic type
        for key, value in NEURAL_PROPERTIES.items():
            setattr(ball, key, value)
        ball.max_hp = NEURAL_PROPERTIES["hp"]

        # Inject the network weights
        ball.nn_weights = population[i].nn.get_weights()
        neural_balls.append(ball)

    # Run the simulation
    sim_instance.run()

    # Calculate fitness
    for i, ball in enumerate(neural_balls):
        # Fitness based on kills and survival (implied by ending HP and being alive)
        survival_bonus = 50.0 if ball.alive else 0.0
        hp_bonus = ball.get_hp_percent() * 20.0
        kill_score = ball.kills * 30.0

        population[i].fitness = survival_bonus + hp_bonus + kill_score

def breed(parent1: Agent, parent2: Agent, mutation_rate: float) -> Agent:
    """Crossover and mutate to create a child."""
    child_nn = NeuralNetwork(5, 8, 7)

    w1 = parent1.nn.get_weights()
    w2 = parent2.nn.get_weights()

    child_weights = copy.deepcopy(w1)

    # Simple crossover: randomly pick weights from parent 1 or 2
    for i in range(len(child_weights["weights_ih"])):
        for j in range(len(child_weights["weights_ih"][i])):
            if random.random() > 0.5:
                child_weights["weights_ih"][i][j] = w2["weights_ih"][i][j]

    for i in range(len(child_weights["weights_ho"])):
        for j in range(len(child_weights["weights_ho"][i])):
            if random.random() > 0.5:
                child_weights["weights_ho"][i][j] = w2["weights_ho"][i][j]

    child_nn.set_weights(child_weights)
    child_nn.mutate(mutation_rate)

    return Agent(child_nn)

def train(generations: int, population_size: int, ticks: int, output_file: str):
    print(f"Starting training: {generations} generations, pop size {population_size}, {ticks} ticks/round")

    # Initialize random population
    population = [Agent(NeuralNetwork(5, 8, 7)) for _ in range(population_size)]

    best_fitness_overall = -1
    best_nn_overall = None

    for gen in range(generations):
        evaluate_population(population, ticks)

        # Sort by fitness (descending)
        population.sort(key=lambda a: a.fitness, reverse=True)

        best_fitness = population[0].fitness
        avg_fitness = sum(a.fitness for a in population) / population_size

        if best_fitness > best_fitness_overall:
            best_fitness_overall = best_fitness
            best_nn_overall = population[0].nn
            # Save the best weights
            best_nn_overall.save(output_file)

        print(f"Gen {gen+1}/{generations} | Best Fit: {best_fitness:.1f} | Avg Fit: {avg_fitness:.1f} | Overall Best: {best_fitness_overall:.1f}")

        # Next generation
        new_population = [Agent(best_nn_overall)] # Elitism: keep best

        # Breed the rest
        while len(new_population) < population_size:
            # Tournament selection
            tournament = random.sample(population[:population_size//2], 3)
            tournament.sort(key=lambda a: a.fitness, reverse=True)
            parent1 = tournament[0]

            tournament = random.sample(population[:population_size//2], 3)
            tournament.sort(key=lambda a: a.fitness, reverse=True)
            parent2 = tournament[0]

            child = breed(parent1, parent2, mutation_rate=0.1)
            new_population.append(child)

        population = new_population

    print(f"Training complete. Best weights saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train BallBrain Neural Networks")
    parser.add_argument("--generations", type=int, default=10, help="Number of generations to train")
    parser.add_argument("--population", type=int, default=20, help="Population size per generation")
    parser.add_argument("--ticks", type=int, default=1000, help="Simulation ticks per generation")
    parser.add_argument("--output", type=str, default="src/ai/nn_weights.json", help="Output file for best weights")

    args = parser.parse_args()

    train(args.generations, args.population, args.ticks, args.output)
