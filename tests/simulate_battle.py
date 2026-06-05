"""
Ball Royale — Battle Simulation Engine
Simulates 50-1000 balls fighting without rendering.
Tests AI logic, performance, and emergent behavior.
"""

import random
import math
import time
import sys
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_brain import BallBrain


BALL_TYPES = {
    "warrior": {"hp": 120, "speed": 2.0, "damage": 15, "radius": 12,
                "perception_radius": 250, "aggression": 0.9, "color": "red",
                "skill": "wave_attack", "skill_cooldown": 5.0},
    "tank": {"hp": 200, "speed": 1.2, "damage": 8, "radius": 18,
             "perception_radius": 200, "aggression": 0.5, "color": "gray",
             "skill": "shield", "skill_cooldown": 8.0},
    "assassin": {"hp": 70, "speed": 3.5, "damage": 25, "radius": 8,
                 "perception_radius": 300, "aggression": 0.8, "color": "purple",
                 "skill": "dash", "skill_cooldown": 3.0},
    "healer": {"hp": 80, "speed": 1.8, "damage": 5, "radius": 10,
               "perception_radius": 350, "aggression": 0.2, "color": "green",
               "skill": "heal_ally", "skill_cooldown": 4.0},
    "sniper": {"hp": 60, "speed": 1.5, "damage": 35, "radius": 9,
               "perception_radius": 500, "aggression": 0.6, "color": "blue",
               "skill": "precision_shot", "skill_cooldown": 6.0},
    "bomber": {"hp": 90, "speed": 1.8, "damage": 20, "radius": 14,
               "perception_radius": 200, "aggression": 0.7, "color": "orange",
               "skill": "explosion", "skill_cooldown": 7.0},
    "berserker": {"hp": 100, "speed": 2.2, "damage": 20, "radius": 13,
                  "perception_radius": 220, "aggression": 1.0, "color": "crimson",
                  "skill": "rage_burst", "skill_cooldown": 5.5},
    "juggernaut": {"hp": 300, "speed": 0.8, "damage": 30, "radius": 22,
                   "perception_radius": 150, "aggression": 0.4, "color": "darkred",
                   "skill": "ground_pound", "skill_cooldown": 8.0},
}


@dataclass
class Vec2:
    x: float = 0.0
    y: float = 0.0

    def distance_to(self, other: 'Vec2') -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy  # squared for speed

    def direction_to(self, other: 'Vec2') -> Tuple[float, float]:
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.001:
            return (0.0, 0.0)
        return (dx / dist, dy / dist)

    def move_towards(self, target: 'Vec2', speed: float, delta: float) -> None:
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.001:
            return
        nx, ny = dx / dist, dy / dist
        step = speed * delta * 60
        if step >= dist:
            self.x, self.y = target.x, target.y
        else:
            self.x += nx * step
            self.y += ny * step


@dataclass
class Booster:
    x: float
    y: float
    kind: str = "health"
    value: float = 20.0
    active: bool = True


@dataclass
class Ball:
    id: int
    ball_type: str
    x: float
    y: float
    hp: float
    max_hp: float
    speed: float
    damage: float
    radius: float
    perception_radius: float
    aggression: float
    color: str
    skill: str
    skill_cooldown: float
    skill_timer: float = 0.0
    alive: bool = True
    kills: int = 0
    current_action: str = "idle"
    personality: str = "idle"

    def get_hp_percent(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def flee(self, delta): self.current_action = "flee"
    def attack(self, delta): self.current_action = "attack"
    def defend(self, delta): self.current_action = "defend"
    def collect_booster(self, delta): self.current_action = "opportunistic"
    def idle(self, delta): self.current_action = "idle"


class SpatialGrid:
    """Spatial hash grid for O(1) neighbor lookups instead of O(N)."""

    def __init__(self, width: float, height: float, cell_size: float = 200.0):
        self.cell_size = cell_size
        self.cols = int(width / cell_size) + 1
        self.rows = int(height / cell_size) + 1
        self.cells: Dict[int, List[Ball]] = {}

    def _key(self, x: float, y: float) -> int:
        col = int(x / self.cell_size)
        row = int(y / self.cell_size)
        return row * self.cols + col

    def clear(self):
        self.cells.clear()

    def insert(self, ball: Ball):
        key = self._key(ball.x, ball.y)
        if key not in self.cells:
            self.cells[key] = []
        self.cells[key].append(ball)

    def get_nearby(self, x: float, y: float, radius: float) -> List[Ball]:
        result = []
        min_col = max(0, int((x - radius) / self.cell_size))
        max_col = min(self.cols - 1, int((x + radius) / self.cell_size))
        min_row = max(0, int((y - radius) / self.cell_size))
        max_row = min(self.rows - 1, int((y + radius) / self.cell_size))
        r2 = radius * radius
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                key = row * self.cols + col
                for ball in self.cells.get(key, []):
                    dx = ball.x - x
                    dy = ball.y - y
                    if dx * dx + dy * dy <= r2:
                        result.append(ball)
        return result


class BattleSimulation:
    def __init__(self, num_balls: int = 100, arena_size: float = 2000.0,
                 max_ticks: int = 3000, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)

        self.width = arena_size
        self.height = arena_size
        self.balls: List[Ball] = []
        self.boosters: List[Booster] = []
        self.max_ticks = max_ticks
        self.num_balls = num_balls
        self.grid = SpatialGrid(arena_size, arena_size)
        self.tick = 0
        self.kill_log = []
        self.stats = {
            "ticks": 0, "total_kills": 0, "survivors": 0, "winner": None,
            "battle_duration": 0.0, "actions_performed": Counter(),
            "ball_types_alive": Counter(), "ball_types_killed": Counter(),
            "longest_killstreak": 0, "avg_hp_at_end": 0.0,
        }

        self._spawn_balls()
        self._spawn_boosters(num_balls // 5)

    def _spawn_balls(self):
        types = list(BALL_TYPES.keys())
        for i in range(self.num_balls):
            bt = random.choice(types)
            cfg = BALL_TYPES[bt]
            r = cfg["radius"] * 2
            self.balls.append(Ball(
                id=i, ball_type=bt,
                x=random.uniform(r, self.width - r),
                y=random.uniform(r, self.height - r),
                hp=cfg["hp"], max_hp=cfg["hp"], speed=cfg["speed"],
                damage=cfg["damage"], radius=cfg["radius"],
                perception_radius=cfg["perception_radius"],
                aggression=cfg["aggression"], color=cfg["color"],
                skill=cfg["skill"], skill_cooldown=cfg["skill_cooldown"],
            ))

    def _spawn_boosters(self, count: int):
        for _ in range(count):
            self.boosters.append(Booster(
                x=random.uniform(50, self.width - 50),
                y=random.uniform(50, self.height - 50),
                kind=random.choice(["health", "damage", "speed"]),
                value=random.uniform(10, 30),
            ))

    def _rebuild_grid(self):
        self.grid.clear()
        for b in self.balls:
            if b.alive:
                self.grid.insert(b)

    def get_nearby_entities(self, ball, radius):
        """Acts as the world interface for perception system."""
        nearby_balls = self.grid.get_nearby(ball.x, ball.y, radius)
        enemies = [b for b in nearby_balls if b.id != ball.id]

        nearby_boosters = []
        for bo in self.boosters:
            if bo.active:
                dx = bo.x - ball.x
                dy = bo.y - ball.y
                if dx * dx + dy * dy <= radius ** 2:
                    nearby_boosters.append(bo)

        return {
            "enemies": enemies,
            "allies": [], # Teams not implemented in base simulation yet
            "boosters": nearby_boosters,
            "traps": []
        }

    def _tick(self):
        self.tick += 1
        self._rebuild_grid()

        for ball in self.balls:
            if not ball.alive:
                continue

            brain = BallBrain(ball, self)
            perception_data = brain.perception()
            emotion = brain.emotion(perception_data)
            decision = brain.decision(perception_data, emotion)

            ball.current_action = decision
            self.stats["actions_performed"][decision] += 1

            # Use perception data for easier access
            enemies = perception_data.get("enemies", [])

            # Movement
            if decision == "flee" and enemies:
                nearest = min(enemies, key=lambda e: (e.x - ball.x) ** 2 + (e.y - ball.y) ** 2)
                dx, dy = ball.x - nearest.x, ball.y - nearest.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0.01:
                    ball.x += (dx / dist) * ball.speed * self._delta * 60
                    ball.y += (dy / dist) * ball.speed * self._delta * 60

            elif decision == "attack" and enemies:
                target = min(enemies, key=lambda e: (e.x - ball.x) ** 2 + (e.y - ball.y) ** 2)
                dx, dy = target.x - ball.x, target.y - ball.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0.01:
                    nx, ny = dx / dist, dy / dist
                    step = ball.speed * self._delta * 60
                    ball.x += nx * min(step, dist)
                    ball.y += ny * min(step, dist)
                if dist <= ball.radius + target.radius + 5:
                    self._deal_damage(ball, target)

            elif decision == "opportunistic":
                active_boosters = [b for b in self.boosters if b.active]
                if active_boosters:
                    nearest = min(active_boosters, key=lambda b: (b.x - ball.x) ** 2 + (b.y - ball.y) ** 2)
                    dx, dy = nearest.x - ball.x, nearest.y - ball.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist > 0.01:
                        nx, ny = dx / dist, dy / dist
                        step = ball.speed * self._delta * 60
                        ball.x += nx * min(step, dist)
                        ball.y += ny * min(step, dist)
                    if dist <= ball.radius + 10:
                        self._collect_booster(ball, nearest)

            else:
                ball.x += random.uniform(-1, 1) * ball.speed * 0.3
                ball.y += random.uniform(-1, 1) * ball.speed * 0.3

            ball.x = max(ball.radius, min(self.width - ball.radius, ball.x))
            ball.y = max(ball.radius, min(self.height - ball.radius, ball.y))

            if ball.skill_timer > 0:
                ball.skill_timer -= self._delta

        if self.tick % 30 == 0:
            active = sum(1 for b in self.boosters if b.active)
            if active < self.num_balls // 10:
                for _ in range(3):
                    self.boosters.append(Booster(
                        x=random.uniform(50, self.width - 50),
                        y=random.uniform(50, self.height - 50),
                        kind=random.choice(["health", "damage", "speed"]),
                        value=random.uniform(10, 30),
                    ))

    def _deal_damage(self, attacker: Ball, target: Ball):
        target.hp -= attacker.damage
        if target.hp <= 0:
            target.alive = False
            attacker.kills += 1
            self.stats["total_kills"] += 1
            self.stats["ball_types_killed"][target.ball_type] += 1
            self.kill_log.append({
                "tick": self.tick, "killer_id": attacker.id,
                "killer_type": attacker.ball_type,
                "victim_id": target.id, "victim_type": target.ball_type,
            })

    def _collect_booster(self, ball: Ball, booster: Booster):
        if booster.kind == "health":
            ball.hp = min(ball.max_hp, ball.hp + booster.value)
        elif booster.kind == "damage":
            ball.damage += booster.value * 0.1
        elif booster.kind == "speed":
            ball.speed += booster.value * 0.01
        booster.active = False

    def run(self) -> Dict:
        self._delta = 0.016
        start = time.time()

        for _ in range(self.max_ticks):
            alive = sum(1 for b in self.balls if b.alive)
            if alive <= 1:
                break
            self._tick()

        elapsed = time.time() - start
        alive_balls = [b for b in self.balls if b.alive]

        self.stats["ticks"] = self.tick
        self.stats["survivors"] = len(alive_balls)
        self.stats["battle_duration"] = round(elapsed, 3)
        self.stats["winner"] = alive_balls[0].ball_type if alive_balls else None
        if alive_balls:
            self.stats["avg_hp_at_end"] = round(sum(b.hp for b in alive_balls) / len(alive_balls), 1)
        for b in self.balls:
            if b.alive:
                self.stats["ball_types_alive"][b.ball_type] += 1

        if self.kill_log:
            streak = 1
            cur = self.kill_log[0]["killer_id"]
            for e in self.kill_log[1:]:
                if e["killer_id"] == cur:
                    streak += 1
                    self.stats["longest_killstreak"] = max(self.stats["longest_killstreak"], streak)
                else:
                    streak = 1
                    cur = e["killer_id"]

        return self.stats

    def print_report(self):
        s = self.stats
        print(f"\n{'='*60}")
        print("  BALL ROYALE — BATTLE SIMULATION REPORT")
        print(f"{'='*60}")
        print(f"  Balls: {self.num_balls}  Arena: {self.width:.0f}x{self.height:.0f}")
        print(f"  Ticks: {s['ticks']}  Duration: {s['battle_duration']}s")
        print(f"  Kills: {s['total_kills']}  Survivors: {s['survivors']}  Winner: {s['winner'] or 'Nobody'}")
        print(f"  Avg HP (end): {s['avg_hp_at_end']}  Killstreak: {s['longest_killstreak']}")
        if s['ball_types_alive']:
            print("  Alive by type:", dict(s['ball_types_alive']))
        print(f"{'='*60}")


# ─── Tests ────────────────────────────────────────────────────────────────────

def test_simulation_50_balls():
    sim = BattleSimulation(num_balls=50, max_ticks=500, seed=42)
    stats = sim.run()
    assert stats["ticks"] > 0
    assert stats["total_kills"] > 0
    sim.print_report()

def test_simulation_200_balls():
    sim = BattleSimulation(num_balls=200, max_ticks=300, seed=123)
    stats = sim.run()
    assert stats["total_kills"] > 10
    assert stats["battle_duration"] < 30
    sim.print_report()

def test_simulation_500_balls():
    sim = BattleSimulation(num_balls=500, max_ticks=200, seed=456)
    stats = sim.run()
    assert stats["total_kills"] > 0
    sim.print_report()

def test_simulation_1000_balls():
    sim = BattleSimulation(num_balls=1000, max_ticks=150, seed=789)
    stats = sim.run()
    assert stats["ticks"] > 0
    sim.print_report()

def test_simulation_deterministic():
    s1 = BattleSimulation(num_balls=50, max_ticks=200, seed=42).run()
    s2 = BattleSimulation(num_balls=50, max_ticks=200, seed=42).run()
    assert s1["total_kills"] == s2["total_kills"]

def test_all_ball_types_represented():
    sim = BattleSimulation(num_balls=100, max_ticks=200, seed=99)
    stats = sim.run()
    represented = set(stats["ball_types_alive"].keys()) | set(stats["ball_types_killed"].keys())
    assert len(represented) >= 6

def test_battle_reduces_to_few():
    sim = BattleSimulation(num_balls=50, max_ticks=1000, seed=42)
    stats = sim.run()
    alive = sum(1 for b in sim.balls if b.alive)
    assert alive < 50, f"Battle should reduce ball count, got {alive}"


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print(f"Running simulation with {n} balls...")
    sim = BattleSimulation(num_balls=n, max_ticks=1000, seed=42)
    stats = sim.run()
    sim.print_report()
