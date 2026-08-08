import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest

from ai.game_modes import GameMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.projectiles = []
        self.dead_balls = []

    def add_event(self, kind, data):
        self.events.append({"type": kind, **data})

def test_supply_drop_midair_shoot_down():
    mode = GameMode()
    world = MockWorld()

    class Hazard:
        def __init__(self, kind, x, y, radius):
            self.kind = kind
            self.x = x
            self.y = y
            self.radius = radius

    drop = Hazard("supply_drop", 100, 100, 40)
    world.arena.hazards.append(drop)

    class Projectile:
        def __init__(self, x, y, active=True):
            self.x = x
            self.y = y
            self.active = active
            self.radius = 10.0

    proj = Projectile(100, 100)
    world.projectiles.append(proj)

    mode.tick(world, [])

    assert not proj.active
    assert drop not in world.arena.hazards

    events = [e for e in world.events if e.get("type") == "supply_drop_shot_down"]
    assert len(events) == 1

    boosters_spawned = [h for h in world.arena.hazards if getattr(h, "kind", "") in ["stamina_booster", "vision_booster", "nemesis_booster", "healing_spring"]]
    assert len(boosters_spawned) >= 3
