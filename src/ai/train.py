import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ai.neural_trainer import NeuralTrainer
from tests.simulate_battle import BattleSimulation

def train_networks(generations=10, population_size=20, ticks=500):
    input_size = 4 # hp_percent, danger_level, opportunity_score, threat_level
    output_size = 8 # flee, defend, collect_booster, attack, chase, use_skill, kite, flank
    trainer = NeuralTrainer(population_size=population_size, input_size=input_size, output_size=output_size)

    weights_path = os.path.join(os.path.dirname(__file__), "nn_weights.json")
    if os.path.exists(weights_path):
        print(f"Loading existing population from {weights_path}")
        # Need to implement load logic for whole population, for now let's just train from scratch or load one
        pass

    print(f"Starting training for {generations} generations...")

    for gen in range(generations):
        fitness_scores = []

        print(f"--- Generation {gen+1}/{generations} ---")

        for i, net in enumerate(trainer.population):
            # Run simulation
            sim = BattleSimulation(num_balls=10, max_ticks=ticks, arena_size=1000)

            # Make sure balls use our network
            from ai.neural_network_brain import NeuralNetworkBrain
            for ball in sim.balls:
                ball.ball_type = "neural"
                ball.nn_weights = net.weights
                ball.nn_biases = net.biases
                # Use NeuralNetworkBrain directly since BallBrain no longer has built-in neural fallback
                sim.brains[ball.id] = NeuralNetworkBrain(ball, sim)

            # Run
            sim.run()

            # Calculate fitness
            total_fitness = 0.0
            for ball in sim.balls:
                score = ball.kills * 100.0
                if ball.alive:
                    score += 50.0
                    score += ball.get_hp_percent() * 50.0
                total_fitness += score

            avg_fitness = total_fitness / max(1, len(sim.balls))
            fitness_scores.append(avg_fitness)

        best_score = max(fitness_scores)
        print(f"Generation {gen+1} Best Fitness: {best_score:.2f}")

        # Evolve
        trainer.evolve_generation(fitness_scores, mutation_rate=0.1, mutation_amount=0.5)

    # Save best
    trainer.save_best(fitness_scores, weights_path)
    print(f"Training complete. Best weights saved to {weights_path}")

if __name__ == "__main__":
    train_networks(generations=2)
