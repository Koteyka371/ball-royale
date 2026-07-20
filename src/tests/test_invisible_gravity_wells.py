import pytest
from unittest.mock import MagicMock
from ai.game_modes import InvisibleGravityWellsMode

class MockBall:
    def __init__(self, x, y):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.ball_type = "player"
        self.max_stamina = 100.0
        self.stamina = 100.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.original_base_damage = 10.0
        self.traits = []
        self.weather_immunity_timer = 0.0
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 500.0
        self.invisible = False
        self.speed_multiplier = 1.0

def test_invisible_gravity_wells_spawn():
    mode = InvisibleGravityWellsMode()
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.hazards = []
    world.arena.width = 1000
    world.arena.height = 1000

    # Mock data correctly
    world.leaderboard_manager = MagicMock()
    world.leaderboard_manager.data = MagicMock()
    world.leaderboard_manager.data.get.return_value = 1

    balls = []
    mode.setup(world, balls)

    # Tick past spawn timer
    mode.tick(world, balls, delta=5.1)

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert getattr(hazard, "kind", "") == "invisible_gravity_well"
    assert getattr(hazard, "invisible", False) == True

def test_invisible_gravity_wells_pull():
    mode = InvisibleGravityWellsMode()
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.hazards = []

    world.leaderboard_manager = MagicMock()
    world.leaderboard_manager.data = MagicMock()
    world.leaderboard_manager.data.get.return_value = 1

    class MockHazard:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.kind = "invisible_gravity_well"
            self.radius = 200.0
            self.duration = 10.0

    h = MockHazard(500, 500)
    world.arena.hazards.append(h)

    b = MockBall(550, 500) # Distance 50 from center (dx = 500 - 550 = -50)

    mode.tick(world, [b], delta=1.0)

    # Hazard is at 500, ball is at 550. dx = h.x - b.x = -50.
    # Pull should be negative x.
    assert b.vx < 0
    assert b.vy == 0
