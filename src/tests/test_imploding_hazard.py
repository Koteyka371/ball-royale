import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "warrior"

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

def test_imploding_hazard_mode():
    world = MockWorld()
    mode = GAME_MODES["imploding_hazard"]

    # Fast forward to trigger spawn
    mode.spawn_timer = 0.0
    balls = [MockBall(1, 500, 500)]
    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert getattr(hazard, "kind", "") == "imploding_hazard"

    hazard.x = 500.0
    hazard.y = 500.0

    # Test pulling effect
    b = MockBall(1, 600, 500)
    b.vx = 0.0
    b.vy = 0.0
    mode.tick(world, [b], 0.1)

    assert b.vx < 0 # Pulled towards 500 (left)

    # Fast forward to explosion
    hazard.duration = 0.01

    b2 = MockBall(2, 550, 500)
    b2.vx = 0.0

    mode.tick(world, [b, b2], 0.1)

    # Hazard should be removed
    assert len(world.arena.hazards) == 0

    # Both balls should be pushed
    assert b2.vx > 0

    # Visual effect should be emitted
    assert any(e["type"] == "visual_effect" and e["data"].get("type") == "imploding_hazard_explosion" for e in world.events)
