import sys
import os
import json
import random
import math
import copy

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from tests.simulate_battle import BattleSimulation

# Neural network architecture:
# Inputs (4): hp_percent, danger_level, opportunity_score, threat_level
# Hidden (8): Fully connected, tanh activation
# Outputs (6): flee, defend, collect_booster, attack, chase, use_skill
# Weights size: (4 * 8) + (8 * 6) = 32 + 48 = 80 weights.
# Bias size: 8 + 6 = 14 biases.
# Total size: 94 weights.

class NeuralNetwork:
    def __init__(self, weights=None):
        self.input_size = 4
        self.hidden_size = 8
        self.output_size = 6
        self.num_weights = (self.input_size * self.hidden_size) + self.hidden_size + \
                           (self.hidden_size * self.output_size) + self.output_size

        if weights is None:
            self.weights = [random.uniform(-1.0, 1.0) for _ in range(self.num_weights)]
        else:
            self.weights = list(weights)

    def copy(self):
        return NeuralNetwork(list(self.weights))

    def mutate(self, mutation_rate=0.1, mutation_strength=0.2):
        for i in range(len(self.weights)):
            if random.random() < mutation_rate:
                self.weights[i] += random.uniform(-mutation_strength, mutation_strength)

def evaluate_population(population, ticks=500):
    # Run a battle royale simulation where each Neural ball is assigned a NN from the population.
    # To keep things simple, we'll spawn exactly len(population) Neural balls.

    sim = BattleSimulation(num_balls=len(population), max_ticks=ticks, seed=random.randint(0, 99999))

    # Force all balls to be 'neural'
    for b in sim.balls:
        b.ball_type = "neural"
        b.personality = "neural"
        b.hp = 100
        b.max_hp = 100
        b.speed = 2.2
        b.damage = 15
        b.radius = 10
        b.perception_radius = 300
        b.aggression = 0.5
        b.color = "white"
        b.skill = "dash"
        b.skill_cooldown = 4.0

    # Inject NN weights into balls
    for i, ball in enumerate(sim.balls):
        ball.nn_weights = population[i].weights

    sim.run(record=False)

    # Calculate fitness for each network based on the performance of its ball
    fitnesses = []
    for i, ball in enumerate(sim.balls):
        # Fitness based on survival time (ticks survived) and kills.
        # Note: sim.history doesn't track exact death time easily if we don't record,
        # but we can check if it's alive.
        survival_score = 100 if ball.alive else 0
        kill_score = ball.kills * 50
        damage_taken = ball.max_hp - ball.hp
        hp_score = (ball.hp / ball.max_hp) * 20 if ball.alive else 0

        fitness = survival_score + kill_score + hp_score
        fitnesses.append((population[i], fitness))

    return fitnesses

def crossover(parent1, parent2):
    child_weights = []
    for w1, w2 in zip(parent1.weights, parent2.weights):
        child_weights.append(w1 if random.random() < 0.5 else w2)
    return NeuralNetwork(child_weights)

def train(generations=50, population_size=50, ticks=500):
    population = [NeuralNetwork() for _ in range(population_size)]

    best_overall = None
    best_fitness = -1

    for gen in range(generations):
        fitnesses = evaluate_population(population, ticks)

        # Sort by fitness descending
        fitnesses.sort(key=lambda x: x[1], reverse=True)

        gen_best_nn, gen_best_fitness = fitnesses[0]

        if gen_best_fitness > best_fitness:
            best_fitness = gen_best_fitness
            best_overall = gen_best_nn.copy()

        print(f"Generation {gen+1}/{generations} - Best Fitness: {gen_best_fitness:.2f} - Top Kills: {fitnesses[0][1]}...")

        # Elitism: keep top 20%
        elite_count = int(population_size * 0.2)
        next_population = [x[0].copy() for x in fitnesses[:elite_count]]

        # Breed the rest
        while len(next_population) < population_size:
            p1 = random.choice(fitnesses[:elite_count])[0]
            p2 = random.choice(fitnesses[:elite_count])[0]
            child = crossover(p1, p2)
            child.mutate(mutation_rate=0.1, mutation_strength=0.2)
            next_population.append(child)

        population = next_population

    print(f"Training complete. Best overall fitness: {best_fitness:.2f}")
    return best_overall

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--generations", type=int, default=10)
    parser.add_argument("--population", type=int, default=50)
    parser.add_argument("--ticks", type=int, default=500)
    args = parser.parse_args()

    best_nn = train(generations=args.generations, population_size=args.population, ticks=args.ticks)

    save_path = os.path.join(os.path.dirname(__file__), "nn_weights.json")
    with open(save_path, "w") as f:
        json.dump(best_nn.weights, f)

    print(f"Saved best weights to {save_path}")
