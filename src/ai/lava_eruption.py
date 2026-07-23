from ai.game_modes import GameMode
from typing import Any, List
import random
import math

class LavaEruptionEventMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Lava Eruption Event"
        self.description = "A random event that periodically erupts lava fountains from the ground, leaving damaging puddles that players must navigate around during combat."
        self.eruption_timer = 0.0
        self.eruption_interval = 8.0
        self.eruptions = []
        self.puddles = []

    def apply_dynamic_traits(self, world: 'Any', balls: 'List[Any]', delta: float) -> None:
        super().apply_dynamic_traits(world, balls, delta)

        self.eruption_timer += delta

        if self.eruption_timer >= self.eruption_interval:
            self.eruption_timer = 0.0
            num_eruptions = random.randint(3, 5)
            for _ in range(num_eruptions):
                ex = random.uniform(200.0, 800.0)
                ey = random.uniform(200.0, 800.0)
                self.eruptions.append({
                    "x": ex,
                    "y": ey,
                    "timer": 0.0,
                    "warning_duration": 2.0,
                    "radius": 50.0
                })

        new_eruptions = []
        for e in self.eruptions:
            e["timer"] += delta
            if e["timer"] >= e["warning_duration"]:
                if hasattr(world, "add_event"):
                    world.add_event("lava_eruption", {"x": e["x"], "y": e["y"], "radius": e["radius"]})
                self.puddles.append({
                    "x": e["x"],
                    "y": e["y"],
                    "radius": e["radius"] * 1.5,
                    "duration": 10.0,
                    "timer": 0.0
                })
            else:
                new_eruptions.append(e)
                # Only warn once when it spawns
                if e["timer"] == delta and hasattr(world, "add_event"):
                    world.add_event("lava_warning", {"x": e["x"], "y": e["y"], "radius": e["radius"]})
        self.eruptions = new_eruptions

        new_puddles = []
        for p in self.puddles:
            p["timer"] += delta
            if p["timer"] < p["duration"]:
                new_puddles.append(p)
                for b in balls:
                    if getattr(b, "alive", True):
                        dist = math.hypot(b.x - p["x"], b.y - p["y"])
                        if dist <= p["radius"]:
                            if hasattr(b, "take_damage"):
                                b.take_damage(25.0 * delta)
                            else:
                                b.hp -= 25.0 * delta

                            # Ensure burn_timer attribute is updated (like in lava royale)
                            if not getattr(b, "weather_immunity_timer", 0) > 0:
                                b.burn_timer = getattr(b, "burn_timer", 0.0) + delta

                            if b.hp <= 0:
                                b.hp = 0
                                b.alive = False
        self.puddles = new_puddles
