import json
import os
import sys
import random
import copy
from pathlib import Path
from collections import Counter

# Add parent path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.simulate_battle import BattleSimulation, BALL_TYPES

CONFIG_PATH = Path("src/ai/balance_config.json")
RUNS = 10
BALLS_PER_RUN = 50

def load_current_config():
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    
    # Fallback to defaults from simulate_battle.py
    # We clean up BALL_TYPES to only keep numerical stats we want to mutate
    config = {}
    for b_type, stats in BALL_TYPES.items():
        config[b_type] = {
            "hp": stats["hp"],
            "speed": stats["speed"],
            "damage": stats["damage"],
            "radius": stats["radius"],
            "perception_radius": stats["perception_radius"],
            "aggression": stats["aggression"],
            "skill_cooldown": stats["skill_cooldown"]
        }
    return config

def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def apply_config_to_simulation(config):
    # Overwrite the global BALL_TYPES in tests.simulate_battle
    for b_type, stats in config.items():
        if b_type in BALL_TYPES:
            BALL_TYPES[b_type].update(stats)

def run_simulation_suite() -> float:
    """Runs suite of simulations and returns standard deviation of win rates."""
    wins = Counter()
    total_matches = 0
    
    for i in range(RUNS):
        sim = BattleSimulation(num_balls=BALLS_PER_RUN, max_ticks=1000, seed=100 + i)
        stats = sim.run(record=False)
        winner = stats.get("winner")
        if not winner and stats.get("ball_types_alive"):
            winner = max(stats["ball_types_alive"].items(), key=lambda x: x[1])[0]
        if winner:
            wins[winner] += 1
        total_matches += 1

    # Calculate win rates
    all_types = list(BALL_TYPES.keys())
    rates = [wins.get(t, 0) / total_matches for t in all_types]
    
    # Calculate standard deviation
    mean = sum(rates) / len(rates)
    variance = sum((r - mean) ** 2 for r in rates) / len(rates)
    std_dev = variance ** 0.5
    return std_dev

def mutate_config(config):
    mutated = copy.deepcopy(config)
    
    # Run loop to ensure a value actually changes
    for _ in range(50):
        b_type = random.choice(list(mutated.keys()))
        param = random.choice(["hp", "speed", "damage", "radius", "perception_radius", "aggression", "skill_cooldown"])
        val = mutated[b_type][param]
        
        # Decide mutation size
        if param in ["hp", "radius", "perception_radius"]:
            # Absolute change for integer stats
            delta = random.choice([-5, -2, -1, 1, 2, 5]) if param != "radius" else random.choice([-1, 1])
            new_val = val + delta
        else:
            # Percentage change for float stats
            factor = random.choice([0.9, 0.95, 1.05, 1.1])
            new_val = val * factor
            
        # Boundaries/Constraints to keep it realistic
        if param == "hp":
            new_val = max(30, min(500, new_val))
        elif param == "speed":
            new_val = max(0.5, min(5.0, new_val))
        elif param == "damage":
            new_val = max(2, min(100, new_val))
        elif param == "radius":
            new_val = max(4, min(30, new_val))
        elif param == "perception_radius":
            new_val = max(100, min(600, new_val))
        elif param == "aggression":
            new_val = max(0.1, min(1.0, new_val))
        elif param == "skill_cooldown":
            new_val = max(1.0, min(20.0, new_val))
            
        # Rounding
        if param in ["hp", "radius", "perception_radius"]:
            new_val = int(round(new_val))
        else:
            new_val = round(new_val, 2)
            
        if new_val != val:
            mutated[b_type][param] = new_val
            print(f"[Genetic] Mutated {b_type}.{param}: {val} -> {new_val}")
            return mutated
            
    # Fallback if no change after 50 attempts
    return mutated

def main():
    print("=" * 60)
    print("GENETIC BALANCE TUNER")
    print("=" * 60)
    
    current = load_current_config()
    apply_config_to_simulation(current)
    
    print("[Genetic] Running baseline simulations...")
    baseline_std = run_simulation_suite()
    print(f"[Genetic] Baseline standard deviation of win rates: {baseline_std:.4f}")
    
    # Try 3 different mutations, keep the best one if it improves the balance
    best_config = current
    best_std = baseline_std
    improved = False
    
    for attempt in range(3):
        print(f"\n[Genetic] Mutation attempt {attempt + 1}/3...")
        candidate = mutate_config(best_config)
        apply_config_to_simulation(candidate)
        
        cand_std = run_simulation_suite()
        print(f"[Genetic] Mutated standard deviation: {cand_std:.4f} (best so far: {best_std:.4f})")
        
        if cand_std < best_std:
            best_std = cand_std
            best_config = candidate
            improved = True
            print("[Genetic] Success! Mutation accepted (improved balance).")
        else:
            print("[Genetic] Rejected (worse or equal balance).")
            
    if improved:
        save_config(best_config)
        print("\n[Genetic] New balance configuration saved successfully!")
    else:
        print("\n[Genetic] No improvements found. Keeping current config.")

if __name__ == "__main__":
    main()
