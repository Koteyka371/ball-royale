import cProfile
import pstats
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.simulate_battle import BattleSimulation
from scripts.auto_improve_loop import load_json, save_json, add_task

TASK_FILE = Path("agent_tasks.json")
THRESHOLD_CUMULATIVE_TIME = 0.5  # If a function takes more than 0.5s total time in 100 ticks, flag it

def run_profiler():
    print("[Auto-Profile] Running performance profile on 1000 balls for 100 ticks...")
    
    # Run simulation under profiler
    sim = BattleSimulation(num_balls=1000, max_ticks=100, seed=42)
    
    profiler = cProfile.Profile()
    profiler.enable()
    sim.run(record=False)
    profiler.disable()
    
    # Analyze stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    
    # Extract slow functions
    slow_functions = []
    
    for func, (cc, nc, tt, ct, callers) in stats.stats.items():
        # func is a tuple: (file_name, line_number, function_name)
        file_name, line_num, func_name = func
        
        # We only care about our own code, not Python built-ins or libraries
        if "src/ai/" in file_name or "tests/simulate_battle.py" in file_name:
            if ct > THRESHOLD_CUMULATIVE_TIME:
                short_file = Path(file_name).name
                slow_functions.append({
                    "file": short_file,
                    "func": func_name,
                    "time": ct,
                    "calls": nc
                })
                
    if not slow_functions:
        print("[Auto-Profile] Performance is excellent! No bottlenecks found.")
        return
        
    print(f"[Auto-Profile] Found {len(slow_functions)} performance bottlenecks!")
    
    if not TASK_FILE.exists():
        print("[Auto-Profile] agent_tasks.json not found, aborting.")
        return
        
    manifest = load_json(TASK_FILE)
    modified = False
    
    # Create tasks for the top 3 slowest functions
    slow_functions.sort(key=lambda x: x["time"], reverse=True)
    
    for issue in slow_functions[:3]:
        func_name = issue["func"]
        file_name = issue["file"]
        time_spent = issue["time"]
        calls = issue["calls"]
        
        task_id = f"perf-optimize-{func_name.replace('_', '-')}"
        title = f"Performance: Optimize '{func_name}' in {file_name}"
        desc = (f"The function '{func_name}' in {file_name} is causing a performance bottleneck. "
                f"During a 100-tick stress test, it was called {calls} times and took {time_spent:.2f} seconds total. "
                f"Please optimize this function to reduce its execution time (e.g., use better data structures, caching, or spatial hashing).")
                
        if add_task(manifest, task_id, title, desc, "meta", "high", allowed_paths=[file_name]):
            modified = True
            print(f"  -> Generated task: {task_id}")
            
    if modified:
        save_json(TASK_FILE, manifest)
        print("[Auto-Profile] Tasks saved to backlog.")

if __name__ == "__main__":
    run_profiler()
