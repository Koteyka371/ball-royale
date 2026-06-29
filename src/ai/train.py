import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from ai.neural_trainer import NeuralTrainer # type: ignore
from tests.simulate_battle import BattleSimulation # type: ignore

def train_networks(generations=10, population_size=20, ticks=500, arena_type='procedural', arena_size=1000, custom_scenario=None):
    input_size = 8 # hp_percent, danger_level, opportunity_score, threat_level, distance_to_zone
    output_size = 11 # flee, defend, collect_booster, attack, chase, use_skill, kite, flank, group_attack, hide_behind, hold_zone
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
            num_balls = 10
            if custom_scenario and 'num_balls' in custom_scenario:
                num_balls = custom_scenario['num_balls']

            sim = BattleSimulation(num_balls=num_balls, max_ticks=ticks, arena_size=arena_size, arena_type=arena_type)

            # Apply custom scenario
            if custom_scenario:
                if 'ball_types' in custom_scenario:
                    # Replace opponents with specific types
                    for i, ball in enumerate(sim.balls):
                        if i > 0: # keep ball 0 as our neural network
                            btype = custom_scenario['ball_types'][i % len(custom_scenario['ball_types'])]
                            from tests.simulate_battle import BALL_TYPES
                            if btype in BALL_TYPES:
                                cfg = BALL_TYPES[btype]
                                ball.ball_type = btype
                                ball.hp = ball.max_hp = cfg["hp"]
                                ball.speed = cfg["speed"]
                                ball.damage = cfg["damage"]
                                ball.radius = cfg["radius"]
                                ball.perception_radius = cfg["perception_radius"]
                                ball.aggression = cfg["aggression"]
                                ball.skill = cfg["skill"]
                                ball.skill_cooldown = cfg["skill_cooldown"]

                if 'boosters' in custom_scenario:
                    if custom_scenario['boosters'] == 0:
                        sim.boosters = []

            # Make sure our ball(s) use our network
            from ai.neural_network_brain import NeuralNetworkBrain # type: ignore

            # Decide which balls are the neural ones being trained
            neural_count = 1
            if custom_scenario and 'neural_count' in custom_scenario:
                neural_count = custom_scenario['neural_count']

            for i, ball in enumerate(sim.balls):
                if i < neural_count:
                    ball.ball_type = "neural"
                    ball.nn_weights = net.weights
                    ball.nn_biases = net.biases
                    # Use NeuralNetworkBrain directly
                    sim.brains[ball.id] = NeuralNetworkBrain(ball, sim)

            # Run
            sim.run()

            # Calculate fitness
            total_fitness = 0.0
            neural_balls = [b for b in sim.balls if getattr(b, "ball_type", "") == "neural"]
            if not neural_balls:
                neural_balls = sim.balls[:neural_count]

            for ball in neural_balls:
                score = ball.kills * 100.0

                # Check if in Moving Zone mode
                if getattr(getattr(sim, "game_mode", None), "name", "") == "Moving Zone":
                    score += getattr(ball, "score", 0) * 10.0
                    # Prioritize position over damage
                    score += getattr(ball, "damage_dealt", 0.0) * 0.1
                else:
                    # Active engagement rewards
                    score += getattr(ball, "damage_dealt", 0.0) * 0.5
                    score += getattr(ball, "distance_traveled", 0.0) * 0.05

                    # Survival rewards
                    if ball.alive:
                        score += 50.0
                        score += ball.get_hp_percent() * 50.0

                    # Penalize passive survival
                    if ball.alive and getattr(ball, "damage_dealt", 0.0) == 0 and getattr(ball, "distance_traveled", 0.0) < 500:
                        score -= 50.0

                total_fitness += score

            avg_fitness = total_fitness / max(1, len(neural_balls))
            fitness_scores.append(avg_fitness)

        best_score = max(fitness_scores)
        print(f"Generation {gen+1} Best Fitness: {best_score:.2f}")

        # Evolve
        trainer.evolve_generation(fitness_scores, mutation_rate=0.1, mutation_amount=0.5)

    # Save best
    trainer.save_best(fitness_scores, weights_path)
    print(f"Training complete. Best weights saved to {weights_path}")

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Train neural network balls")
    parser.add_argument("--generations", type=int, default=10, help="Number of generations to train")
    parser.add_argument("--pop", type=int, default=20, help="Population size")
    parser.add_argument("--ticks", type=int, default=500, help="Ticks per simulation")
    parser.add_argument("--arena", type=str, default="procedural", help="Arena type (e.g. procedural, basic)")
    parser.add_argument("--arena-size", type=int, default=1000, help="Size of the arena")
    parser.add_argument("--scenario", type=str, help="JSON string representing a custom scenario")

    args = parser.parse_args()

    scenario = None
    if args.scenario:
        try:
            scenario = json.loads(args.scenario)
            print(f"Using custom scenario: {scenario}")
        except json.JSONDecodeError as e:
            print(f"Error parsing scenario JSON: {e}")
            sys.exit(1)

    train_networks(
        generations=args.generations,
        population_size=args.pop,
        ticks=args.ticks,
        arena_type=args.arena,
        arena_size=args.arena_size,
        custom_scenario=scenario
    )
