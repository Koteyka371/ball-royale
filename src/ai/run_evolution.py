import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from tests.simulate_battle import BattleSimulation
import sys
# Because we append the root dir, ai.genetics needs to be src.ai.genetics
from src.ai.genetics import BallGenetics

def run_evolution(generations=5, num_balls=50):
    print(f"Starting evolutionary simulation with {num_balls} balls over {generations} generations...")

    # Initialize genetics tracker
    genetics = BallGenetics(battles_to_reproduce=2, mutation_rate=0.2, mutation_amount=0.2)

    for gen in range(generations):
        print(f"\n{'='*40}")
        print(f" GENERATION {gen + 1}")
        print(f"{'='*40}")

        # Instantiate battle simulation
        sim = BattleSimulation(num_balls=num_balls, max_ticks=1000, seed=gen)

        # If we have a past generation, overwrite the spawned balls with offspring
        if gen > 0:
            offspring_dna_list = genetics.generate_offspring(num_balls)

            # Apply offspring DNA to the balls that were randomly spawned by the simulator
            for i, ball in enumerate(sim.balls):
                dna = offspring_dna_list[i]
                ball.speed = dna.get("speed", ball.speed)
                ball.damage = dna.get("damage", ball.damage)
                ball.max_hp = dna.get("max_hp", ball.max_hp)
                ball.hp = ball.max_hp
                ball.color = dna.get("color", ball.color)
                ball.skill = dna.get("skill", ball.skill)
                ball.ball_type = dna.get("ball_type", ball.ball_type)

        # Run the simulation
        stats = sim.run(record=False)

        # Gather survivors
        survivors = [b for b in sim.balls if b.alive and getattr(b, "ball_type", None) != "spectator"]
        print(f"Battle finished. Survivors: {len(survivors)}")

        # Register survivors for future reproduction
        if survivors:
            genetics.register_survivors(survivors)

            # Print sample stats of a survivor to see evolution
            sample = survivors[0]
            print(f"Sample Survivor Stats ({sample.ball_type}):")
            print(f"  HP: {sample.max_hp:.1f} | DMG: {sample.damage:.1f} | SPD: {sample.speed:.1f}")
            print(f"  Skill: {sample.skill} | Color: {sample.color}")
        else:
            print("No survivors this generation!")

    print("\nEvolution Simulation Complete.")

if __name__ == "__main__":
    run_evolution(generations=10, num_balls=20)
