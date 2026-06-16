import argparse
import json
import random
import os
import sys

# Ensure tests can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from tests.simulate_battle import BattleSimulation, BALL_TYPES
from src.ai.nn import NeuralNetwork

def mutate(weights, mutation_rate=0.1):
    new_weights = {}
    for key, values in weights.items():
        if isinstance(values[0], list):
            new_weights[key] = [
                [v + random.uniform(-mutation_rate, mutation_rate) if random.random() < 0.2 else v for v in row]
                for row in values
            ]
        else:
            new_weights[key] = [
                v + random.uniform(-mutation_rate, mutation_rate) if random.random() < 0.2 else v
                for v in values
            ]
    return new_weights

def generate_initial_population(size):
    population = []
    for _ in range(size):
        nn = NeuralNetwork(4, 8, 6)
        population.append(nn.get_weights())
    return population

def evaluate_fitness(weights, num_balls=20, ticks=200):
    # Ensure "neural" is a valid ball type for the simulation
    if "neural" not in BALL_TYPES:
        BALL_TYPES["neural"] = {
            "hp": 100, "speed": 2.0, "damage": 15, "radius": 12,
            "perception_radius": 250, "aggression": 0.8, "color": "black",
            "skill": "dash", "skill_cooldown": 4.0
        }

    sim = BattleSimulation(num_balls=num_balls, max_ticks=ticks, arena_size=1000)

    # Inject our weights to all neural balls
    neural_count = 0
    for ball in sim.balls:
        # Forcibly make a fraction of balls "neural" type
        if random.random() < 0.3:
            ball.ball_type = "neural"
            ball.nn_weights = weights
            neural_count += 1

    if neural_count == 0:
        return 0.0

    sim.run(record=False)

    total_fitness = 0.0
    for ball in sim.balls:
        if ball.ball_type == "neural":
            # Fitness: Kills + Survival Bonus
            fitness = ball.kills * 10.0
            if ball.alive:
                fitness += 20.0
            total_fitness += fitness

    return total_fitness / neural_count

def train(generations, population_size, ticks):
    print(f"Starting training: {generations} generations, pop_size {population_size}, {ticks} ticks")

    population = generate_initial_population(population_size)
    best_weights = None
    best_fitness_overall = -float('inf')

    for gen in range(generations):
        fitness_scores = []
        for i, weights in enumerate(population):
            fitness = evaluate_fitness(weights, num_balls=20, ticks=ticks)
            fitness_scores.append((fitness, weights))

        # Sort by fitness (descending)
        fitness_scores.sort(key=lambda x: x[0], reverse=True)
        best_fitness = fitness_scores[0][0]

        print(f"Generation {gen+1}/{generations}: Best Fitness = {best_fitness:.2f}")

        if best_fitness > best_fitness_overall:
            best_fitness_overall = best_fitness
            best_weights = fitness_scores[0][1]

        # Selection and Crossover/Mutation
        top_performers = [w for f, w in fitness_scores[:max(1, population_size // 4)]]

        new_population = []
        new_population.append(top_performers[0]) # Elitism

        while len(new_population) < population_size:
            parent = random.choice(top_performers)
            child = mutate(parent, mutation_rate=0.2)
            new_population.append(child)

        population = new_population

    # Save the best overall weights
    weights_path = os.path.join(os.path.dirname(__file__), "nn_weights.json")
    with open(weights_path, "w") as f:
        json.dump(best_weights, f, indent=2)

    print(f"Training complete. Best weights saved to {weights_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generations", type=int, default=10)
    parser.add_argument("--population", type=int, default=10)
    parser.add_argument("--ticks", type=int, default=200)
    args = parser.parse_args()

    train(args.generations, args.population, args.ticks)
