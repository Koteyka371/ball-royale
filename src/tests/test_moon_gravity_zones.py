import pytest
from unittest.mock import MagicMock
from ai.game_modes import MoonGravityZonesMode

class ArenaMock:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class WorldMock:
    def __init__(self):
        self.arena = ArenaMock()
        self.time = 0.0
        self.weekly_mutator = ''
        self.mutators_active = False
        self.mutators = []

    def add_event(self, event_type, data):
        pass

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 500.0
        self.y = 500.0
        self.radius = 15.0
        self.alive = True
        self.ball_type = "player"
        self.mass = 2.0
        self.bounciness_multiplier = 1.0
        self.vz = 0.0

def test_moon_gravity_zones_spawns_and_applies_effect():
    mode = MoonGravityZonesMode()
    world = WorldMock()
    ball = MockBall()

    # Tick past 10 seconds to spawn zone
    mode.tick(world, [ball], delta=11.0)

    assert len(world.arena.hazards) > 0
    zone = world.arena.hazards[0]

    # Move ball into zone
    ball.x = getattr(zone, "x", 0.0)
    ball.y = getattr(zone, "y", 0.0)

    # Tick to apply effects
    mode.tick(world, [ball], delta=0.1)

    # Should be lightweight
    assert ball.mass == 2.0 * 0.3
    # Should bounce higher
    assert ball.bounciness_multiplier == 2.5
    # vz should increase
    assert ball.vz > 0.0

    # Move ball out
    ball.x = 0.0
    ball.y = 0.0

    mode.tick(world, [ball], delta=0.1)

    # Should restore mass and bounciness
    assert ball.mass == 2.0
    assert ball.bounciness_multiplier == 1.0
