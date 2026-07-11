import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.fly_timer = 2.0

def test_aerial_arena_mode():
    assert "aerial_arena" in GAME_MODES
    mode = GAME_MODES["aerial_arena"]

    world = MockWorld()
    ball1 = MockBall(500, 500)
    balls = [ball1]

    # Test setup
    mode.setup(world, balls)
    bounce_pads = [h for h in world.arena.hazards if getattr(h, "kind", "") == "bounce_pad"]
    assert len(bounce_pads) == 5

    # Test tick
    mode.spawn_timer = 0.0
    mode.tick(world, balls, 0.1)

    aerial_hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") in ["scrambler_drone", "lightning_cloud"]]
    assert len(aerial_hazards) >= 1

    # Force a tick to check logic
    hz = type("Hazard", (), {"id": 1, "x": 500, "y": 500, "radius": 15.0, "kind": "scrambler_drone", "damage": 0.0, "vx": 0.0, "vy": 0.0, "duration": 15.0, "active": True})
    world.arena.hazards.append(hz)

    hz_lightning = type("Hazard", (), {"id": 2, "x": 500, "y": 500, "radius": 80.0, "kind": "lightning_cloud", "damage": 10.0, "vx": 0.0, "vy": 0.0, "duration": 20.0, "active": True})
    world.arena.hazards.append(hz_lightning)

    mode.tick(world, balls, 0.1)
    assert ball1.hp < 100.0, "Ball should have taken damage from lightning cloud because it is airborne (fly_timer > 0)"
