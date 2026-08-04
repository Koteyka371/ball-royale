import pytest
from ai.game_modes import SwappingSafeZoneMode, GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y):
        self.id = id(self)
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "player"
        self.hp = 100.0
        self.damage_taken = 0.0
        self.slow_timer = 0.0

    def take_damage(self, amount, source):
        self.damage_taken += amount

def test_swapping_safe_zone_registered():
    assert "swapping_safe_zone" in GAME_MODES
    assert isinstance(GAME_MODES["swapping_safe_zone"], SwappingSafeZoneMode)

def test_swapping_safe_zone_tick():
    mode = SwappingSafeZoneMode()
    world = MockWorld()

    # inside
    b1 = MockBall(500, 500)
    # outside
    b2 = MockBall(50, 50)
    balls = [b1, b2]

    mode.setup(world, balls)

    assert mode.inside_is_safe == True

    # Tick when inside is safe
    mode.tick(world, balls, delta=1.0)

    # b1 inside, should take no damage
    assert b1.damage_taken == 0
    # b2 outside, should take damage
    assert b2.damage_taken > 0
    assert b2.slow_timer > 0

    # Reset
    b2.damage_taken = 0

    # Tick exactly enough to swap
    mode.tick(world, balls, delta=10.0) # passes swap_interval (10.0)

    assert mode.inside_is_safe == False

    # Now inside is dangerous, b1 should take damage, b2 should be safe
    # But note that `tick` applies damage *after* swapping.
    assert b1.damage_taken > 0
