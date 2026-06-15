import json
import sys
from pathlib import Path
from collections import Counter

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.simulate_battle import BattleSimulation, BALL_TYPES
from scripts.auto_improve_loop import load_json, save_json, add_task

TASK_FILE = Path("agent_tasks.json")
RUNS = 10
BALLS_PER_RUN = 50

def run_balance_check():
    print(f"[Auto-Balance] Running {RUNS} headless simulations with {BALLS_PER_RUN} balls each...")
    
    wins = Counter()
    total_matches = 0
    
    for i in range(RUNS):
        # We use a different seed for each run
        sim = BattleSimulation(num_balls=BALLS_PER_RUN, max_ticks=1000, seed=42 + i)
        stats = sim.run(record=False)
        
        # Determine the winner type (the type that has the most survivors, or the last one alive)
        winner_type = stats.get("winner")
        if not winner_type and stats.get("ball_types_alive"):
            winner_type = max(stats["ball_types_alive"].items(), key=lambda x: x[1])[0]
            
        if winner_type:
            wins[winner_type] += 1
        total_matches += 1
        
        if (i + 1) % 2 == 0:
            print(f"  Completed {i + 1}/{RUNS} runs...")

    if total_matches == 0:
        print("[Auto-Balance] No valid matches completed.")
        return

    print("\n[Auto-Balance] Win Rate Report:")
    win_rates = {}
    for b_type in BALL_TYPES:
        name = b_type if isinstance(b_type, str) else b_type.__name__.lower()
        w_rate = (wins.get(name, 0) / total_matches) * 100
        win_rates[name] = w_rate
        print(f"  {name.ljust(15)}: {w_rate:>5.1f}%")

    # Analyze for severe imbalance
    # Expected win rate is 100 / number of ball types (e.g. 12 types = ~8.3%)
    expected_wr = 100.0 / len(BALL_TYPES)
    overpowered_threshold = expected_wr * 3.0  # e.g. > 25%
    underpowered_threshold = expected_wr * 0.1 # e.g. < 0.8%

    if not TASK_FILE.exists():
        print("[Auto-Balance] agent_tasks.json not found, aborting task generation.")
        return

    manifest = load_json(TASK_FILE)
    modified = False

    for b_type, rate in win_rates.items():
        if rate >= overpowered_threshold:
            task_id = f"balance-nerf-{b_type}"
            title = f"Balance: Nerf overpowered '{b_type}'"
            desc = (f"The '{b_type}' class is winning {rate:.1f}% of the time "
                    f"(expected ~{expected_wr:.1f}%). It is overpowered. "
                    f"Please reduce its HP, damage, speed, or increase skill cooldown.")
            if add_task(manifest, task_id, title, desc, "meta", "medium", acceptance=["Win rate reduced in simulations"]):
                modified = True
                
        elif rate <= underpowered_threshold:
            task_id = f"balance-buff-{b_type}"
            title = f"Balance: Buff underpowered '{b_type}'"
            desc = (f"The '{b_type}' class is winning only {rate:.1f}% of the time "
                    f"(expected ~{expected_wr:.1f}%). It is severely underpowered. "
                    f"Please increase its survivability, damage, speed, or decrease skill cooldown.")
            if add_task(manifest, task_id, title, desc, "meta", "medium", acceptance=["Win rate increased in simulations"]):
                modified = True

    if modified:
        save_json(TASK_FILE, manifest)
        print("\n[Auto-Balance] Successfully created balance adjustment tasks!")
    else:
        print("\n[Auto-Balance] Game looks balanced. No tasks created.")

if __name__ == "__main__":
    run_balance_check()
