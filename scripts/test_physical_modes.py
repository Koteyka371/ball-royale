"""
Automated Physical & Observational Mode Testing Suite.
Monitors 2D physics stability, visual jitter, unnatural teleportation, ball sticking/overlap, and simulation stagnation.
Logs all telemetry anomalies to docs/observability_anomalies.md.
"""

import sys
import os
import math
import traceback
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple


ANOMALY_LOG_FILE = Path("docs/observability_anomalies.md")


class PhysicalModeTester:
    def __init__(self, ticks_per_mode: int = 250, num_balls: int = 16):
        self.ticks_per_mode = ticks_per_mode
        self.num_balls = num_balls

    def _log_anomaly(self, mode_key: str, tick: int, anomaly_type: str, details: str):
        ANOMALY_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not ANOMALY_LOG_FILE.exists():
            with open(ANOMALY_LOG_FILE, "w", encoding="utf-8") as f:
                f.write("# Ball Royale — Physical Observability Anomaly Log\n\n")
                f.write("Log of detected motion jitter, teleportation spikes, overlap sticking, and simulation stagnation.\n\n")

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        entry = f"- **[{now_str}] Mode: `{mode_key}` (Tick {tick})** | Type: `{anomaly_type}` | {details}\n"
        
        with open(ANOMALY_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)

    def test_mode_physics(self, mode_key: str, mode_obj: Any) -> Dict[str, Any]:
        result = {
            "mode": mode_key,
            "passed": True,
            "errors": [],
            "anomalies": [],
            "ticks_run": 0,
            "nan_positions": 0,
            "out_of_bounds": 0,
            "teleports_detected": 0,
            "vibrations_detected": 0,
            "overlaps_detected": 0,
            "deadlocks_detected": 0,
            "winner": None
        }

        try:
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
            from tests.simulate_battle import BattleSimulation # type: ignore
            sim = BattleSimulation(num_balls=self.num_balls, max_ticks=self.ticks_per_mode, seed=42)
            
            if hasattr(sim, "game_mode"):
                sim.game_mode = mode_obj

            sim._delta = 0.016

            prev_positions = {}
            prev_velocities = {}
            vibration_counters = {}
            overlap_counters = {}
            stagnation_ticks = 0
            prev_total_hp = 0

            for t in range(self.ticks_per_mode):
                sim._tick()
                result["ticks_run"] += 1

                alive_balls = [b for b in sim.balls if getattr(b, "alive", True) and getattr(b, "ball_type", None) != "spectator"]
                current_total_hp = sum(getattr(b, "hp", 0) for b in alive_balls)

                # 1. Stagnation / Deadlock check
                if abs(current_total_hp - prev_total_hp) < 0.01:
                    stagnation_ticks += 1
                else:
                    stagnation_ticks = 0
                prev_total_hp = current_total_hp

                if stagnation_ticks > 120 and len(alive_balls) > 1:
                    msg = f"Simulation stagnation detected: zero damage/state change for {stagnation_ticks} ticks"
                    result["anomalies"].append(msg)
                    result["deadlocks_detected"] += 1
                    self._log_anomaly(mode_key, t, "SIMULATION_DEADLOCK", msg)
                    stagnation_ticks = 0

                # 2. Per-ball spatial checks (NaN, Out-of-bounds, Jitter, Teleportation)
                for b in alive_balls:
                    if not hasattr(b, "x") or not hasattr(b, "y"):
                        continue
                    
                    # NaN check
                    if math.isnan(b.x) or math.isnan(b.y) or math.isnan(getattr(b, "vx", 0)) or math.isnan(getattr(b, "vy", 0)):
                        result["nan_positions"] += 1
                        result["passed"] = False
                        result["errors"].append(f"NaN position/velocity detected at tick {t} for ball {b.id}")
                        break

                    # Containment boundary check
                    margin = 150
                    if b.x < -margin or b.x > sim.width + margin or b.y < -margin or b.y > sim.height + margin:
                        result["out_of_bounds"] += 1
                        if result["out_of_bounds"] > 8:
                            result["passed"] = False
                            msg = f"Ball {b.id} escaped arena boundaries at ({b.x:.1f}, {b.y:.1f})"
                            result["errors"].append(msg)
                            self._log_anomaly(mode_key, t, "BOUNDARY_ESCAPE", msg)
                            break

                    # Teleportation & Vibration Jitter Check
                    bid = getattr(b, "id", None)
                    if bid is not None:
                        if bid in prev_positions:
                            px, py = prev_positions[bid]
                            disp = math.sqrt((b.x - px)**2 + (b.y - py)**2)
                            
                            # Teleportation spike without dash/teleport skill
                            skill_name = getattr(b, "skill", "none")
                            max_allowed_disp = getattr(b, "speed", 3.0) * sim._delta * 60.0 * 5.0 + 35.0
                            
                            if disp > max_allowed_disp and skill_name not in ["dash", "teleport", "global_mirage", "blink"]:
                                result["teleports_detected"] += 1
                                msg = f"Unnatural teleportation displacement spike ({disp:.1f}px > {max_allowed_disp:.1f}px) for ball {bid}"
                                result["anomalies"].append(msg)
                                self._log_anomaly(mode_key, t, "TELEPORT_JITTER", msg)

                        if bid in prev_velocities and hasattr(b, "vx") and hasattr(b, "vy"):
                            pvx, pvy = prev_velocities[bid]
                            vx, vy = b.vx, b.vy
                            mag_curr = math.sqrt(vx*vx + vy*vy)
                            mag_prev = math.sqrt(pvx*pvx + pvy*pvy)
                            
                            if mag_curr > 1.0 and mag_prev > 1.0:
                                dot = (vx * pvx + vy * pvy) / (mag_curr * mag_prev)
                                if dot < -0.85:
                                    vibration_counters[bid] = vibration_counters.get(bid, 0) + 1
                                    if vibration_counters[bid] >= 4:
                                        result["vibrations_detected"] += 1
                                        msg = f"High-frequency motion vibration jitter detected for ball {bid}"
                                        result["anomalies"].append(msg)
                                        self._log_anomaly(mode_key, t, "VIBRATION_JITTER", msg)
                                        vibration_counters[bid] = 0
                                else:
                                    vibration_counters[bid] = max(0, vibration_counters.get(bid, 0) - 1)

                        prev_positions[bid] = (b.x, b.y)
                        prev_velocities[bid] = (getattr(b, "vx", 0), getattr(b, "vy", 0))

                # 3. Ball Overlap / Sticking Check
                for i in range(len(alive_balls)):
                    for j in range(i + 1, len(alive_balls)):
                        b1, b2 = alive_balls[i], alive_balls[j]
                        r1 = getattr(b1, "radius", 12)
                        r2 = getattr(b2, "radius", 12)
                        dist = math.sqrt((b1.x - b2.x)**2 + (b1.y - b2.y)**2)
                        
                        pair_key = (min(b1.id, b2.id), max(b1.id, b2.id))
                        if dist < 0.55 * (r1 + r2):
                            overlap_counters[pair_key] = overlap_counters.get(pair_key, 0) + 1
                            if overlap_counters[pair_key] >= 10:
                                result["overlaps_detected"] += 1
                                msg = f"Unnatural ball sticking/overlap between balls {pair_key[0]} & {pair_key[1]} ({dist:.1f}px < {r1+r2}px)"
                                result["anomalies"].append(msg)
                                self._log_anomaly(mode_key, t, "OVERLAP_STICKING", msg)
                                overlap_counters[pair_key] = 0
                        else:
                            overlap_counters[pair_key] = max(0, overlap_counters.get(pair_key, 0) - 1)

                if not result["passed"]:
                    break

            result["winner"] = getattr(sim, "winner", "TBD")

        except Exception as e:
            result["passed"] = False
            result["errors"].append(f"Runtime Exception in mode '{mode_key}': {e}\n{traceback.format_exc()}")

        return result

    def run_all_modes(self, sample_count: int = None) -> bool:
        print("=" * 60)
        print("PHYSICAL & OBSERVATIONAL MODE TESTING SUITE")
        print("=" * 60)
        
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
        from ai.game_modes import GAME_MODES # type: ignore
        mode_items = list(GAME_MODES.items())
        if sample_count and sample_count < len(mode_items):
            import random
            mode_items = random.sample(mode_items, sample_count)
            print(f"[*] Sampling {sample_count} out of {len(GAME_MODES)} registered game modes for fast observation...")
        else:
            print(f"[*] Testing all {len(GAME_MODES)} registered game modes...")

        all_passed = True

        for key, mode_obj in mode_items:
            res = self.test_mode_physics(key, mode_obj)
            status_str = "[PASS]" if res["passed"] else "[FAIL]"
            anom_count = len(res["anomalies"])
            anom_str = f"| Anomalies: {anom_count}" if anom_count > 0 else ""
            
            print(f"  {status_str} Mode: {key:<25} | Ticks: {res['ticks_run']:<4} {anom_str}")
            
            if not res["passed"]:
                all_passed = False
                for err in res["errors"]:
                    print(f"         Error: {err.splitlines()[0]}")

        print("-" * 60)
        if all_passed:
            print("[SUCCESS] Physical observation & jitter testing completed successfully!")
        else:
            print("[WARNING] Physical observation failures detected in one or more modes.")

        print("=" * 60)
        return all_passed


def main():
    sample_fast = "--fast" in sys.argv or "--sample" in sys.argv
    tester = PhysicalModeTester(ticks_per_mode=150, num_balls=10)
    success = tester.run_all_modes(sample_count=10 if sample_fast else None)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
