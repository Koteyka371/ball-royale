"""
Ball Royale — AI Performance Benchmark
Measures how many balls can be processed within 16ms (60 FPS target).
"""

import time
import sys
import os
import statistics
from typing import List, Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_brain import BallBrain


class MockBall:
    def __init__(self, hp=100, max_hp=100, personality="idle"):
        self.hp = hp
        self.max_hp = max_hp
        self.personality = personality
        self.current_action = None
        self.x = 0.0
        self.y = 0.0

    def get_hp_percent(self):
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def flee(self, delta): pass
    def attack(self, delta): pass
    def defend(self, delta): pass
    def collect_booster(self, delta): pass
    def idle(self, delta): pass


class MockWorld:
    def __init__(self):
        self.entities = {"enemies": [], "allies": [], "boosters": []}

    def get_nearby_entities(self, ball, radius):
        return self.entities


def benchmark_brain_tick(num_balls: int, num_iterations: int = 100) -> Dict:
    balls = [MockBall(hp=100, max_hp=100) for _ in range(num_balls)]
    world = MockWorld()
    world.entities["enemies"] = [MockBall() for _ in range(num_balls // 3)]
    world.entities["boosters"] = [1] * (num_balls // 10)

    brains = [BallBrain(b, world) for b in balls]

    times = []
    for _ in range(num_iterations):
        start = time.perf_counter()
        for brain in brains:
            brain.process(0.016)
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)

    avg_ms = statistics.mean(times)
    p95_ms = sorted(times)[int(len(times) * 0.95)]
    max_ms = max(times)
    fps = 1000.0 / avg_ms if avg_ms > 0 else float('inf')
    ms_per_ball = avg_ms / num_balls if num_balls > 0 else 0

    return {
        "num_balls": num_balls,
        "avg_ms": round(avg_ms, 3),
        "p95_ms": round(p95_ms, 3),
        "max_ms": round(max_ms, 3),
        "fps": round(fps, 1),
        "ms_per_ball": round(ms_per_ball, 4),
        "target_60fps": avg_ms < 16.0,
    }


def find_max_balls_for_60fps(max_test: int = 2000, step: int = 50) -> int:
    last_good = 0
    for n in range(step, max_test + step, step):
        result = benchmark_brain_tick(n, num_iterations=20)
        status = "OK" if result["target_60fps"] else "SLOW"
        print(f"  {n:5d} balls: {result['avg_ms']:7.2f}ms avg, {result['fps']:6.1f} FPS [{status}]")
        if result["target_60fps"]:
            last_good = n
        else:
            break
    return last_good


def run_benchmark_suite() -> Dict:
    print("\n" + "=" * 60)
    print("  BALL ROYALE — AI PERFORMANCE BENCHMARK")
    print("=" * 60)

    results = {}
    for count in [10, 50, 100, 200, 500, 1000]:
        result = benchmark_brain_tick(count, num_iterations=50)
        results[count] = result
        status = "PASS" if result["target_60fps"] else "FAIL"
        print(f"  {count:5d} balls: {result['avg_ms']:7.2f}ms avg, {result['fps']:6.1f} FPS [{status}]")

    print("\n  --- Max balls for 60 FPS ---")
    max_balls = find_max_balls_for_60fps(max_test=2000, step=100)
    print(f"\n  Result: {max_balls} balls at 60 FPS")

    results["max_60fps"] = max_balls
    results["pass"] = results[100]["target_60fps"]

    print("=" * 60)
    return results


if __name__ == "__main__":
    results = run_benchmark_suite()
    if results.get("pass"):
        print("BENCHMARK PASSED")
        sys.exit(0)
    else:
        print("BENCHMARK FAILED — AI too slow for 60 FPS at 100 balls")
        sys.exit(1)
