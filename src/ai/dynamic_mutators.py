import random
import math
from ai.game_modes import GameMode

class DynamicWeatherMutatorsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Dynamic Weather Mutators"
        self.description = "Cycles through thunderstorm, blizzard, and sandstorm every 10 seconds."
        self.weather_timer = 10.0
        self.lightning_timer = 2.0
        self.current_weather = "blizzard"
        self.weathers = ["thunderstorm", "blizzard", "sandstorm"]

    def setup(self, world, balls):
        super().setup(world, balls)
        self.current_weather = random.choice(self.weathers)
        self.weather_timer = 10.0
        self.lightning_timer = 2.0

        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                b.base_speed = getattr(b, "base_speed", getattr(b, "speed", 100.0))
                b.base_perception_radius = getattr(b, "base_perception_radius", getattr(b, "perception_radius", 250.0))

        if not hasattr(world, "arena"):
            class MockArena:
                hazards = []
            world.arena = MockArena()
        if not hasattr(world.arena, "hazards"):
            world.arena.hazards = []

    def tick(self, world, balls, delta=0.016):
        super().tick(world, balls, delta)

        self.weather_timer -= delta
        if self.weather_timer <= 0:
            self.weather_timer = 10.0
            self.current_weather = random.choice(self.weathers)

        if self.current_weather == "thunderstorm":
            self.lightning_timer -= delta
            if self.lightning_timer <= 0:
                self.lightning_timer = 2.0
                if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                    class LightningStrike:
                        pass
                    strike = LightningStrike()
                    strike.kind = "lightning_strike"
                    strike.x = random.uniform(100, 700)
                    strike.y = random.uniform(100, 500)
                    strike.radius = 40.0
                    strike.damage = 30.0
                    strike.duration = 0.5
                    world.arena.hazards.append(strike)

        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                base_speed = getattr(b, "base_speed", 100.0)
                base_perc = getattr(b, "base_perception_radius", 250.0)

                if self.current_weather == "blizzard":
                    b.speed = base_speed * 0.5
                    b.perception_radius = base_perc
                elif self.current_weather == "sandstorm":
                    b.speed = base_speed
                    b.perception_radius = base_perc * 0.3
                else:
                    b.speed = base_speed
                    b.perception_radius = base_perc

        active_hazards = []
        if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
            for hazard in world.arena.hazards:
                keep_hazard = True
                if getattr(hazard, "kind", "") == "lightning_strike":
                    hazard.duration -= delta
                    if hazard.duration <= 0:
                        keep_hazard = False
                    else:
                        for b in balls:
                            if getattr(b, "alive", True):
                                dx = b.x - hazard.x
                                dy = b.y - hazard.y
                                if math.hypot(dx, dy) < hazard.radius:
                                    dmg = hazard.damage * delta
                                    if hasattr(b, "take_damage"):
                                        b.take_damage(dmg)
                                    else:
                                        b.hp -= dmg
                                        if b.hp <= 0:
                                            b.alive = False
                if keep_hazard:
                    active_hazards.append(hazard)
            world.arena.hazards = active_hazards
