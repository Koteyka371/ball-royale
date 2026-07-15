import pytest
from ai.game_modes import GameMode, PeriodicSafeZoneMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.name = "default"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "player"
        self.hp = 100.0
        self.damage_taken = 0.0

    def take_damage(self, amount, source):
        self.damage_taken += amount

def test_periodic_safe_zone_mode():
    mode = PeriodicSafeZoneMode()
    world = MockWorld()

    b1 = MockBall(500, 500) # Center
    b2 = MockBall(50, 50)   # Edge
    balls = [b1, b2]

    mode.setup(world, balls)
    assert mode.phase == "waiting"
    assert mode.zone_radius == 750.0

    mode.tick(world, balls, delta=1.0)
    assert mode.phase == "waiting"
    assert mode.damage_multiplier == 1.0
    assert b1.damage_taken == 0

    # Ensure b2 is clearly outside
    b2.x = -500
    b2.y = -500
    b2.damage_taken = 0.0
    mode.tick(world, balls, delta=1.0)
    assert b2.damage_taken > 0

    # Fast forward waiting time
    mode.tick(world, balls, delta=14.0)
    assert mode.phase == "shrinking"
    assert mode.damage_multiplier == 1.5

    # Tick during shrink
    mode.tick(world, balls, delta=5.0)
    assert mode.phase == "shrinking"

    # Complete shrink
    mode.tick(world, balls, delta=5.0)
    assert mode.phase == "waiting"
