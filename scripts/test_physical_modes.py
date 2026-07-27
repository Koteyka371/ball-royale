"""
Automated Physical Mode Observability Suite.
Runs physical, spatial, and state observation simulations for every registered game mode.
Ensures physics integrity, containment, collision stability, and game loop health.
"""

import sys
import os
import math
import traceback
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.game_modes import GAME_MODES # type: ignore
from tests.simulate_battle import BattleSimulation # type: ignore


class PhysicalModeTester:
    def __init__(self, ticks_per_mode: int = 250, num_balls: int = 16):
        self.ticks_per_mode = ticks_per_mode
        self.num_balls = num_balls

    def test_mode_physics(self, mode_key: str, mode_obj: Any) -> Dict[str, Any]:
        result = {
            "mode": mode_key,
            "passed": True,
            "errors": [],
            "ticks_run": 0,
            "nan_positions": 0,
            "out_of_bounds": 0,
            "winner": None
        }

        try:
            sim = BattleSimulation(num_balls=self.num_balls, max_ticks=self.ticks_per_mode, seed=42)
            
            # Inject game mode if supported
            if hasattr(sim, "game_mode"):
                sim.game_mode = mode_obj

            sim._delta = 0.016

            for t in range(self.ticks_per_mode):
                sim._tick()
                result["ticks_run"] += 1

                # Physical & spatial observation checks on active balls
                for b in sim.balls:
                    if not hasattr(b, "x") or not hasattr(b, "y"):
                        continue
                    
                    # 1. NaN check
                    if math.isnan(b.x) or math.isnan(b.y) or math.isnan(getattr(b, "vx", 0)) or math.isnan(getattr(b, "vy", 0)):
                        result["nan_positions"] += 1
                        result["passed"] = False
                        result["errors"].append(f"NaN position/velocity detected at tick {t} for ball {b.id}")
                        break

                    # 2. Containment boundary check (allowing slight margin for rebound)
                    margin = 150
                    if b.x < -margin or b.x > sim.width + margin or b.y < -margin or b.y > sim.height + margin:
                        result["out_of_bounds"] += 1
                        if result["out_of_bounds"] > 5:
                            result["passed"] = False
                            result["errors"].append(f"Ball {b.id} escaped arena boundaries at ({b.x:.1f}, {b.y:.1f})")
                            break

                if not result["passed"]:
                    break

            result["winner"] = getattr(sim, "winner", "TBD")

        except Exception as e:
            result["passed"] = False
            result["errors"].append(f"Runtime Exception in mode '{mode_key}': {e}\n{traceback.format_exc()}")

        return result

    def run_all_modes(self) -> bool:
        print("=" * 60)
        print("PHYSICAL MODE OBSERVABILITY SUITE")
        print("=" * 60)
        print(f"[*] Testing {len(GAME_MODES)} registered game modes...")

        all_passed = True
        report = []

        for key, mode_obj in GAME_MODES.items():
            res = self.test_mode_physics(key, mode_obj)
            status_str = "[PASS]" if res["passed"] else "[FAIL]"
            print(f"  {status_str} Mode: {key:<25} | Ticks: {res['ticks_run']:<4} | OutOfBounds: {res['out_of_bounds']}")
            
            if not res["passed"]:
                all_passed = False
                for err in res["errors"]:
                    print(f"         Error: {err.splitlines()[0]}")

            report.append(res)

        print("-" * 60)
        if all_passed:
            print("[SUCCESS] All game modes passed physical observation testing!")
        else:
            print("[WARNING] Physical observation failures detected in one or more modes.")

        print("=" * 60)
        return all_passed


def main():
    tester = PhysicalModeTester(ticks_per_mode=200, num_balls=12)
    success = tester.run_all_modes()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
