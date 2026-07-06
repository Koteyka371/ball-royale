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
from typing import List, Dict, Optional, Tuple, Any
from system.crowd_system import CrowdSystem
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.ball_brain import BallBrain # type: ignore
from ai.neural_network_brain import NeuralNetworkBrain # type: ignore
from arena.arena_types import get_arena # type: ignore


BALL_TYPES = {
        "payload": {"hp": 2000, "speed": 0.5, "damage": 0, "radius": 20,
                "perception_radius": 0, "aggression": 0.0, "color": "white",
                "skill": "none", "skill_cooldown": 999.0},
    "necromancer": {"hp": 90, "speed": 2.0, "damage": 15, "radius": 10,
                    "perception_radius": 320, "aggression": 0.3, "color": "black",
                    "skill": "raise_dead", "skill_cooldown": 8.0},
    "void_mage": {"hp": 100, "speed": 2.0, "damage": 10, "radius": 10,
                  "perception_radius": 300, "aggression": 0.5, "color": "purple",
                  "skill": "black_hole_summon", "skill_cooldown": 10.0},
    "warrior": {"hp": 120, "speed": 2.0, "damage": 15, "radius": 12,
                "perception_radius": 250, "aggression": 0.9, "color": "red",
                "skill": "wave_attack", "skill_cooldown": 5.0},
    "tank": {"hp": 200, "speed": 1.2, "damage": 8, "radius": 18,
             "perception_radius": 200, "aggression": 0.5, "color": "gray",
             "skill": "shield", "skill_cooldown": 8.0},
    "assassin": {"hp": 70, "speed": 3.5, "damage": 25, "radius": 8,
                 "perception_radius": 300, "aggression": 0.8, "color": "purple",
                 "skill": "dash", "skill_cooldown": 3.0},
    "mirage": {"hp": 80, "speed": 4.0, "damage": 10, "radius": 10,
               "perception_radius": 300, "aggression": 0.3, "color": "lightblue",
               "skill": "global_mirage", "skill_cooldown": 15.0},
    "healer": {"hp": 120, "speed": 2.2, "damage": 5, "radius": 10,
               "perception_radius": 350, "aggression": 0.2, "color": "green",
               "skill": "health_link", "skill_cooldown": 2.5},
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
    "phantom": {"hp": 65, "speed": 3.0, "damage": 22, "radius": 8,
                "perception_radius": 320, "aggression": 0.7, "color": "cyan",
                "skill": "phase_through", "skill_cooldown": 4.0},
    "rogue": {"hp": 75, "speed": 2.8, "damage": 18, "radius": 10,
              "perception_radius": 280, "aggression": 0.75, "color": "brown",
              "skill": "steal_boost", "skill_cooldown": 4.5},
    "swarm": {"hp": 60, "speed": 3.8, "damage": 15, "radius": 6,
              "perception_radius": 200, "aggression": 0.6, "color": "lime",
              "skill": "clone", "skill_cooldown": 6.0},
    "guardian": {"hp": 400, "speed": 2.2, "damage": 25, "radius": 16,
                 "perception_radius": 220, "aggression": 0.8, "color": "gold",
                 "skill": "protect_ally", "skill_cooldown": 3.0},
    "scout": {"hp": 80, "speed": 3.8, "damage": 20, "radius": 9,
              "perception_radius": 350, "aggression": 0.5, "color": "lightblue",
              "skill": "dash", "skill_cooldown": 3.5},
    "king": {"hp": 150, "speed": 1.8, "damage": 10, "radius": 14,
             "perception_radius": 300, "aggression": 0.2, "color": "gold",
             "skill": "command", "skill_cooldown": 5.0},
    "ninja": {"hp": 65, "speed": 4.5, "damage": 25, "radius": 8,
              "perception_radius": 350, "aggression": 0.8, "color": "black",
              "skill": "stealth", "skill_cooldown": 4.0},
    "paladin": {"hp": 180, "speed": 3.0, "damage": 15, "radius": 14, "perception_radius": 220, "aggression": 0.6, "color": "gold", "skill": "holy_shield", "skill_cooldown": 6.0},
    "mage": {"hp": 80, "speed": 2.5, "damage": 25, "radius": 10, "perception_radius": 300, "aggression": 0.5, "color": "blue", "skill": "fireball", "skill_cooldown": 4.5},
    "warlock": {"hp": 100, "speed": 2.2, "damage": 20, "radius": 11, "perception_radius": 280, "aggression": 0.7, "color": "purple", "skill": "life_drain", "skill_cooldown": 5.0},
    "druid": {"hp": 130, "speed": 2.8, "damage": 12, "radius": 12, "perception_radius": 260, "aggression": 0.4, "color": "darkgreen", "skill": "entangle", "skill_cooldown": 5.5},
    "monk": {"hp": 110, "speed": 3.5, "damage": 18, "radius": 11, "perception_radius": 240, "aggression": 0.5, "color": "orange", "skill": "chi_blast", "skill_cooldown": 3.5},
    "brawler": {"hp": 160, "speed": 3.2, "damage": 22, "radius": 13, "perception_radius": 200, "aggression": 0.9, "color": "brown", "skill": "uppercut", "skill_cooldown": 4.0},
        "payload": {"hp": 2000, "speed": 0.5, "damage": 0, "radius": 20,
                "perception_radius": 0, "aggression": 0.0, "color": "white",
                "skill": "none", "skill_cooldown": 999.0},
    "necromancer": {"hp": 90, "speed": 2.0, "damage": 15, "radius": 10, "perception_radius": 320, "aggression": 0.3, "color": "black", "skill": "raise_dead", "skill_cooldown": 8.0},
    "trickster": {"hp": 85, "speed": 4.0, "damage": 14, "radius": 9, "perception_radius": 270, "aggression": 0.6, "color": "pink", "skill": "illusion", "skill_cooldown": 4.0},
    "elementalist": {"hp": 95, "speed": 2.6, "damage": 24, "radius": 10, "perception_radius": 290, "aggression": 0.5, "color": "cyan", "skill": "elemental_burst", "skill_cooldown": 5.0},
    "vampire": {"hp": 120, "speed": 3.8, "damage": 18, "radius": 11, "perception_radius": 250, "aggression": 0.8, "color": "darkred", "skill": "bite", "skill_cooldown": 4.0},
    "templar": {"hp": 170, "speed": 2.5, "damage": 16, "radius": 15, "perception_radius": 230, "aggression": 0.7, "color": "white", "skill": "smite", "skill_cooldown": 5.5},
    "ranger": {"hp": 105, "speed": 3.0, "damage": 20, "radius": 10, "perception_radius": 350, "aggression": 0.5, "color": "green", "skill": "multishot", "skill_cooldown": 4.5},
    "spectator": {"hp": 99999, "speed": 5.0, "damage": 0, "radius": 5,
                  "perception_radius": 1000, "aggression": 0.0, "color": "white",
                  "skill": "observe", "skill_cooldown": 1.0},
    "mimic": {"hp": 100, "speed": 2.0, "damage": 10, "radius": 10, "perception_radius": 250, "aggression": 0.5, "color": "magenta", "skill": "none", "skill_cooldown": 5.0},
    "chaos": {"hp": 100, "speed": 3.0, "damage": 15, "radius": 10,
              "perception_radius": 250, "aggression": 0.5, "color": "magenta",
              "skill": "random", "skill_cooldown": 2.0},
    "hard": {"hp": 150, "speed": 3.5, "damage": 20, "radius": 11,
             "perception_radius": 300, "aggression": 0.8, "color": "darkred",
             "skill": "perfect_strike", "skill_cooldown": 4.0}
}

import json  # noqa: E402
try:
    _config_path = os.path.join(os.path.dirname(__file__), "../src/ai/balance_config.json")
    if os.path.exists(_config_path):
        with open(_config_path, "r", encoding="utf-8") as _f:
            _custom_cfg = json.load(_f)
            for _k, _v in _custom_cfg.items():
                if _k in BALL_TYPES:
                    BALL_TYPES[_k].update(_v)
except Exception:
    pass



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
    skin: str = "default"
    skill_timer: float = 0.0
    alive: bool = True
    kills: int = 0
    distance_traveled: float = 0.0
    damage_dealt: float = 0.0
    first_hit_taken: bool = False
    current_action: str = "idle"
    personality: str = "idle"


    is_minion: bool = False
    minion_owner: int = -1
    time_since_death: float = 0.0
    copied_skill: str = ""
    mimic_targets: dict = field(default_factory=dict)
    copy_duration_required: float = 3.0

    def _copy_stats_from(self, enemy):
        self.max_hp = self.max_hp * 0.5 + enemy.max_hp * 0.5
        self.hp = self.hp * 0.5 + enemy.hp * 0.5

        base_s = getattr(self, "base_speed", getattr(self, "speed", 2.0))
        target_speed = getattr(enemy, "speed", 2.0)
        self.base_speed = base_s * 0.5 + target_speed * 0.5
        self.speed = self.base_speed

        base_d = getattr(self, "base_damage", getattr(self, "damage", 10.0))
        target_damage = getattr(enemy, "damage", 10.0)
        self.base_damage = base_d * 0.5 + target_damage * 0.5
        self.damage = self.base_damage

        self.copied_skill = getattr(enemy, "skill", "none")
        self.skill = self.copied_skill

    def process_mimicry(self, enemies, delta: float):
        if self.copied_skill:
            return

        for e in enemies:
            dist_sq = (e.x - self.x)**2 + (e.y - self.y)**2
            if dist_sq < 2500:
                if getattr(self, "mimic_targets", None) is None:
                    self.mimic_targets = {}
                if e.id not in self.mimic_targets:
                    self.mimic_targets[e.id] = 0.0
                self.mimic_targets[e.id] += delta

                if self.mimic_targets[e.id] >= self.copy_duration_required:
                    self._copy_stats_from(e)
                    break
            elif getattr(self, "mimic_targets", None) and e.id in self.mimic_targets:
                self.mimic_targets[e.id] = max(0.0, self.mimic_targets[e.id] - delta * 0.5)

    def notify_kill(self, victim):
        if not getattr(self, "copied_skill", ""):
            self._copy_stats_from(victim)
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
        import math
        if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
            return 0
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
        import math
        result: List[Ball] = []
        if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
            return result
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
    def __init__(self, num_balls: int = 100, arena_size: float = 2000.0, arena_type: str = "procedural",
                 max_ticks: int = 3000, seed: Optional[int] = None, use_neural: bool = False):
        if seed is not None:
            random.seed(seed)

        self.width = arena_size
        self.height = arena_size
        self.arena = get_arena(arena_type, arena_size, seed=seed)
        self.balls: List[Ball] = []
        self.dead_balls: List[Ball] = []
        self.boosters: List[Booster] = []
        self.max_ticks = max_ticks
        self.num_balls = num_balls
        self.grid = SpatialGrid(arena_size, arena_size)
        self.brains: Dict[int, Any] = {}  # ball_id -> BallBrain, created once per ball
        self.tick = 0
        self.crowd_system = CrowdSystem(self)
        self.use_neural = use_neural
        self.kill_log: List[Dict[str, Any]] = []
        self.death_coordinates: List[Dict[str, float]] = []
        self.stats: Dict[str, Any] = {
            "ticks": 0, "total_kills": 0, "survivors": 0, "winner": None,
            "battle_duration": 0.0, "actions_performed": Counter(),
            "ball_types_alive": Counter(), "ball_types_killed": Counter(),
            "longest_killstreak": 0, "avg_hp_at_end": 0.0,
        }

        self._spawn_balls()
        self._spawn_boosters(num_balls // 5)

        # Create brains once for each ball (persistent across ticks)
        for ball in self.balls:
            if self.use_neural and ball.id % 2 == 0:
                ball.brain_type = "neural"  # type: ignore
                self.brains[ball.id] = NeuralNetworkBrain(ball, self)
            else:
                ball.brain_type = "standard"  # type: ignore
                self.brains[ball.id] = BallBrain(ball, self)

    def _spawn_balls(self):
        types = list(BALL_TYPES.keys())
        for i in range(self.num_balls):
            bt = random.choice(types)
            cfg = BALL_TYPES[bt]
            r = cfg["radius"] * 2
            spawn_x, spawn_y = self.arena.get_random_spawn_point(r)
            self.balls.append(Ball(
                id=i, ball_type=bt,
                x=spawn_x,
                y=spawn_y,
                hp=cfg["hp"], max_hp=cfg["hp"], speed=cfg["speed"],
                damage=cfg["damage"], radius=cfg["radius"],
                perception_radius=cfg["perception_radius"],
                aggression=cfg["aggression"], color=cfg["color"],
                skill=cfg["skill"], skill_cooldown=cfg["skill_cooldown"],
                skin=cfg.get("skin", "default"),
            ))

    def _spawn_boosters(self, count: int):
        for _ in range(count):
            spawn_x, spawn_y = self.arena.get_random_spawn_point(10)
            self.boosters.append(Booster(
                x=spawn_x,
                y=spawn_y,
                kind=random.choice(["health", "damage", "speed"]),
                value=random.uniform(10, 30),
            ))

    def _rebuild_grid(self):
        self.grid.clear()
        import math
        for b in self.balls:
            if b.alive:
                if math.isnan(b.x) or math.isinf(b.x):
                    b.x = self.width / 2
                if math.isnan(b.y) or math.isinf(b.y):
                    b.y = self.height / 2
                self.grid.insert(b)

    def get_nearby_entities(self, ball, radius):
        """Implement world interface for Perception layer."""
        nearby_balls = self.grid.get_nearby(ball.x, ball.y, radius)
        enemies = []
        allies = []

        for b in nearby_balls:
            if b.id != ball.id and getattr(b, "ball_type", None) != "spectator":
                if getattr(b, "ball_type", None) == getattr(ball, "ball_type", None):
                    allies.append(b)
                else:
                    enemies.append(b)

        boosters = []
        for bo in self.boosters:
            if bo.active:
                dx = bo.x - ball.x
                dy = bo.y - ball.y
                if dx * dx + dy * dy <= radius ** 2:
                    boosters.append(bo)

        return {
            "enemies": enemies,
            "allies": allies,
            "boosters": boosters,
            "traps": []   # No traps in this simulation yet
        }

    def _tick(self):
        self.tick += 1
        self.crowd_system.tick(self.balls, self.kill_log, self.tick)
        self._rebuild_grid()

        for ball in self.balls:
            if not ball.alive:
                if ball in self.dead_balls:
                    ball.time_since_death += self._delta
                else:
                    ball.time_since_death = 0.0
                    self.dead_balls.append(ball)
                continue

            brain = self.brains.get(ball.id)
            if not brain:
                continue

            brain.process(self._delta)

            # Action Layer will set ball.current_action, record stats
            self.stats["actions_performed"][ball.current_action] += 1

        if self.tick % 30 == 0:
            active = sum(1 for b in self.boosters if b.active)
            if active < self.num_balls // 10:
                for _ in range(3):
                    rx, ry = self.arena.get_random_spawn_point(10)
                    self.boosters.append(Booster(
                        x=rx,
                        y=ry,
                        kind=random.choice(["health", "damage", "speed"]),
                        value=random.uniform(10, 30),
                    ))

    def _deal_damage(self, attacker: Ball, target: Ball):
        if getattr(target, "ball_type", None) == "spectator":
            return
        if target.hp == target.max_hp and attacker.damage > 0:
            target.first_hit_taken = True

        actual_damage = min(target.hp, attacker.damage)
        target.hp -= actual_damage
        if hasattr(attacker, "damage_dealt"):
            attacker.damage_dealt += actual_damage

        if target.hp <= 0:
            target.alive = False
            attacker.kills += 1
            self.stats["total_kills"] += 1
            self.stats["ball_types_killed"][target.ball_type] += 1

            if hasattr(attacker, 'notify_kill'):
                attacker.notify_kill(target)
            self.death_coordinates.append({"x": target.x, "y": target.y})
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

    def add_event(self, event_type: str, data: dict):
        if hasattr(event_type, "get") and "type" in event_type:
            data = event_type
            event_type = data["type"]

        if event_type == "audio_event":
            pass # print(f"[AUDIO] {data.get('sound')} (vol: {data.get('volume')})")
        elif event_type == "crowd_cheer":
            pass # print(f"[CROWD] {data.get('message')}")
        elif event_type == "crowd_throw":
            pass # print(f"[CROWD] {data.get('message')}")
        elif event_type == "spawn_booster":
            try:
                from arena.procedural_arena import Item # type: ignore
                new_item = Item(id=getattr(self, "next_id", 9999), x=data.get('x', 0), y=data.get('y', 0), kind=data.get('kind', 'speed'), value=data.get('value', 30.0))
                if hasattr(self, 'arena') and hasattr(self.arena, 'items'):
                    self.arena.items.append(new_item)
                elif hasattr(self, 'items'):
                    self.items.append(new_item)
                if hasattr(self, "next_id"):
                    self.next_id += 1
            except Exception:
                pass

        if event_type == "weather_warning":
            self.kill_log.append({
                "tick": self.tick,
                "type": "weather_warning",
                "message": data.get("message", "Weather event!")
            })
        elif event_type == "weather_change":
            self.kill_log.append({
                "tick": self.tick,
                "type": "weather_change",
                "weather": data.get("weather", "clear")
            })

        elif event_type in ["crowd_cheer", "crowd_throw"]:
            self.kill_log.append({
                "tick": self.tick,
                "type": event_type,
                "message": data.get("message", "Crowd event!")
            })
        elif event_type == "audio_event":
            self.kill_log.append({
                "tick": self.tick,
                "type": "audio_event",
                "sound": data.get("sound", "unknown_sound"),
                "volume": data.get("volume", 1.0)
            })
        elif event_type == "spawn_booster":
            rx, ry = self.arena.get_random_spawn_point(10)
            x = data.get("x", rx)
            y = data.get("y", ry)
            kind = data.get("kind", random.choice(["health", "damage", "speed"]))
            value = data.get("value", 50.0)
            self.boosters.append(Booster(x=x, y=y, kind=kind, value=value))

    def set_coach_strategy(self, strategy):
        self.coach_strategy = strategy

    def run(self, record: bool = False) -> Dict:
        self._delta = 0.016
        start = time.time()
        self.history = []

        for _ in range(self.max_ticks):
            alive = sum(1 for b in self.balls if b.alive and getattr(b, "ball_type", None) != "spectator")
            if alive <= 1:
                break
            self._tick()

            if record:
                frame_balls = []
                for b in self.balls:
                    if b.alive:
                        frame_balls.append({
                            "id": b.id,
                            "type": b.ball_type,
                            "x": round(b.x, 1),
                            "y": round(b.y, 1),
                            "hp": round(b.hp, 1),
                            "max_hp": b.max_hp,
                            "action": b.current_action,
                            "color": b.color
                        })
                frame_boosters = []
                for bo in self.boosters:
                    if bo.active:
                        frame_boosters.append({
                            "x": round(bo.x, 1),
                            "y": round(bo.y, 1),
                            "kind": bo.kind
                        })
                frame_hazards = []
                if hasattr(self.arena, "hazards"):
                    for h in self.arena.hazards:
                        if getattr(h, "active", True):
                            frame_hazards.append({
                                "id": h.id,
                                "x": round(h.x, 1),
                                "y": round(h.y, 1),
                                "radius": round(h.radius, 1),
                                "kind": h.kind
                            })
                self.history.append({
                    "tick": self.tick,
                    "balls": frame_balls,
                    "boosters": frame_boosters,
                    "hazards": frame_hazards
                })

        elapsed = time.time() - start
        alive_balls = [b for b in self.balls if b.alive]

        self.stats["ticks"] = self.tick
        self.stats["survivors"] = len(alive_balls)
        self.stats["battle_duration"] = round(elapsed, 3)
        self.stats["winner"] = alive_balls[0].ball_type if alive_balls else None

        # Profile integration
        try:
            from system.profile import ProfileManager # type: ignore
            pm = ProfileManager("profile.json")
            pm.add_skill_points(10)  # Reward player 10 points for finishing a match
        except Exception:
            pass
        if alive_balls:
            self.stats["avg_hp_at_end"] = round(sum(b.hp for b in alive_balls) / len(alive_balls), 1)
        for b in self.balls:
            if b.alive:
                self.stats["ball_types_alive"][b.ball_type] += 1

        if self.kill_log:
            streak = 1
            cur = self.kill_log[0].get("killer_id", None)
            for e in self.kill_log[1:]:
                k_id = e.get("killer_id", None)
                if k_id is not None and k_id == cur:
                    streak += 1
                    self.stats["longest_killstreak"] = max(self.stats["longest_killstreak"], streak)
                else:
                    streak = 1
                    cur = k_id

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

        if hasattr(self, 'kill_log') and self.kill_log:
            try:
                import os
                import sys
                sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
                from ai.commentator import BattleCommentator # type: ignore
                from ui.stats_overlay import StatsOverlay # type: ignore
                commentator = BattleCommentator()
                lines = commentator.generate_commentary(self.kill_log, self.stats)
                print(f"\n{'='*60}")
                print("  BATTLE COMMENTARY")
                print(f"{'='*60}")
                for line in lines[-10:]:
                    print(f"  > {line}")
                print(f"{'='*60}")

                print("\n" + "="*60)
                print("  UI KILL FEED PREVIEW")
                print("="*60)
                for msg in commentator.kill_feed.get_messages():
                    print(f"  [UI] {msg}")

                print("\n" + "="*60)
                print("  UI STATS OVERLAY PREVIEW")
                print("="*60)

                overlay = StatsOverlay()
                kills_by_id = {}
                for log in self.kill_log:
                    kid = log.get("killer_id")
                    if kid is not None:
                        kills_by_id[kid] = kills_by_id.get(kid, 0) + 1

                overlay.update([{"id": b.id, "type": b.ball_type, "hp": b.hp, "kills": kills_by_id.get(b.id, 0)} for b in self.balls])
                for line in overlay.format_text().split("\n"):
                    print(f"  [UI] {line}")
                print("\n" + "="*60)
                print("  UI HEATMAP OVERLAY PREVIEW")
                print("="*60)
                try:
                    from ui.heatmap.heatmap import HeatmapOverlay # type: ignore
                    heatmap = HeatmapOverlay()
                    heatmap.update(self.death_coordinates)
                    heatmap.render_to_console()
                except ImportError:
                    pass
            except ImportError:
                pass


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
    sim.run()
    alive = sum(1 for b in sim.balls if b.alive)
    assert alive < 50, f"Battle should reduce ball count, got {alive}"


if __name__ == "__main__":
    import argparse
    import json
    from video.highlight_detector import HighlightDetector # type: ignore

    parser = argparse.ArgumentParser(description="Run Ball Royale Battle Simulation.")
    parser.add_argument("num_balls", type=int, nargs="?", default=100, help="Number of balls.")
    parser.add_argument("--export", type=str, default="", help="Path to export JSON replay file.")
    parser.add_argument("--ticks", type=int, default=1000, help="Max ticks for battle.")
    parser.add_argument("--eval-neural", action="store_true", help="Evaluate NeuralNetworkBrain over 500 battles.")
    args = parser.parse_args()

    if args.eval_neural:
        print("Running NeuralNetworkBrain Evaluation (500 Battles)...")
        neural_wins = 0
        standard_wins = 0
        neural_kills = 0
        standard_kills = 0
        neural_survivors = 0
        standard_survivors = 0

        for i in range(500):
            sim = BattleSimulation(num_balls=args.num_balls, max_ticks=args.ticks, seed=i, use_neural=True)
            stats = sim.run(record=False)

            # Count kills
            for log in sim.kill_log:
                killer_id = log["killer_id"]
                # Find the killer brain type
                killer = next((b for b in sim.balls if b.id == killer_id), None)
                if killer:
                    if getattr(killer, "brain_type", "standard") == "neural":
                        neural_kills += 1
                    else:
                        standard_kills += 1

            # Check survivors and winner
            alive_balls = [b for b in sim.balls if b.alive]
            for b in alive_balls:
                if getattr(b, "brain_type", "standard") == "neural":
                    neural_survivors += 1
                else:
                    standard_survivors += 1

            if len(alive_balls) == 1:
                winner = alive_balls[0]
                if getattr(winner, "brain_type", "standard") == "neural":
                    neural_wins += 1
                else:
                    standard_wins += 1
            elif len(alive_balls) > 1:
                # If time ran out, the side with more survivors "wins"
                n_surv = sum(1 for b in alive_balls if getattr(b, "brain_type", "standard") == "neural")
                s_surv = len(alive_balls) - n_surv
                if n_surv > s_surv:
                    neural_wins += 1
                elif s_surv > n_surv:
                    standard_wins += 1

            if (i + 1) % 50 == 0:
                print(f"Completed {i + 1}/500 battles...")

        print("\n" + "="*60)
        print("  NEURAL NETWORK BRAIN EVALUATION REPORT (500 Battles)")
        print("="*60)
        print(f"  Neural Wins:   {neural_wins} ({(neural_wins/500)*100:.1f}%)")
        print(f"  Standard Wins: {standard_wins} ({(standard_wins/500)*100:.1f}%)")
        print(f"  Draws:         {500 - neural_wins - standard_wins}")
        print("\n  Total Kills:")
        print(f"    Neural:   {neural_kills}")
        print(f"    Standard: {standard_kills}")
        print("\n  Total Survivors at end of battles:")
        print(f"    Neural:   {neural_survivors}")
        print(f"    Standard: {standard_survivors}")
        print("="*60)
        import sys
        sys.exit(0)

    print(f"Running simulation with {args.num_balls} balls...")
    sim = BattleSimulation(num_balls=args.num_balls, max_ticks=args.ticks, seed=42)
    
    record = bool(args.export)
    stats = sim.run(record=record)
    sim.print_report()
    if args.export:
        detector = HighlightDetector()
        highlights = detector.detect_highlights(sim.history, sim.kill_log)

        replay_data = {
            "arena": {
                "width": sim.width,
                "height": sim.height
            },
            "ball_types": BALL_TYPES,
            "kill_log": sim.kill_log,
            "death_coordinates": sim.death_coordinates,
            "history": sim.history,
            "highlights": highlights
        }
        try:
            with open(args.export, "w", encoding="utf-8") as f:
                json.dump(replay_data, f, indent=2)
            print(f"Replay successfully exported to: {args.export}")
        except Exception as e:
            print(f"Error exporting replay: {e}")
