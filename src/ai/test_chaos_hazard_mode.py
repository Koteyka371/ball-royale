import pytest
import math
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 20.0
        self.damage = 20.0
        self.base_max_hp = 200.0
        self.max_hp = 200.0
        self.hp = 200.0
        self.is_alive = True

def test_chaos_hazard_mode():
    mode = GAME_MODES.get("chaos_hazard")
    assert mode is not None

    world = type("World", (), {})()
    world.arena = type("Arena", (), {"width": 800, "height": 600, "hazards": []})()

    # Ball 1 inside, Ball 2 outside
    b1 = MockBall(1, 400, 300) # center
    b2 = MockBall(2, 750, 550) # outside
    balls = [b1, b2]

    mode.setup(world, balls)

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.get("kind") == "chaos_hazard"
    assert hazard.get("x") == 400.0
    assert hazard.get("y") == 300.0

    # Tick below interval, nothing changes
    mode.tick(world, balls, delta=1.5)
    assert b1.speed == 100.0
    assert b1.damage == 20.0
    assert b1.max_hp == 200.0

    # Force mutation by ticking past interval
    mode.tick(world, balls, delta=0.6)

    # Check if ball 1 has changed stats
    changed_stats = sum([
        b1.speed != 100.0,
        b1.damage != 20.0,
        b1.max_hp != 200.0
    ])
    assert changed_stats >= 1, "At least one stat should be mutated for ball inside hazard"

    # Check if ball 2 stats remain unchanged
    assert b2.speed == 100.0
    assert b2.damage == 20.0
    assert b2.max_hp == 200.0

    # Further check that HP scales correctly when max_hp changes
    if b1.max_hp != 200.0:
        expected_hp = b1.max_hp * (200.0 / 200.0) # original hp ratio was 1.0
        assert math.isclose(b1.hp, expected_hp)
