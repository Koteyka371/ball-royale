import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.speed = 100.0
        self.perception_radius = 100.0
        self.base_perception_radius = 100.0
        self.projectile_speed_multiplier = 1.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []

def test_sniper_towers_mode():
    mode = GAME_MODES["sniper_towers"]
    world = MockWorld()

    ball = MockBall(500, 500)
    balls = [ball]

    mode.tower_spawn_timer = 0.0
    mode.tick(world, balls, delta=0.1)

    assert len(mode.towers) > 0
    assert len(world.events) > 0
    assert world.events[-1]["type"] == "tower_rise"

    mode.towers = [{"x": 500, "y": 500, "radius": 50.0}]
    mode.tick(world, balls, delta=0.1)

    assert getattr(ball, "_on_tower", False) == True
    assert ball.speed == 0.0
    assert ball.perception_radius == 500.0
    assert ball.projectile_speed_multiplier == 5.0

    mode.towers = [{"x": 100, "y": 100, "radius": 50.0}]
    mode.tick(world, balls, delta=0.1)

    assert getattr(ball, "_on_tower", False) == False
    assert ball.speed == 100.0
    assert ball.perception_radius == 100.0
    assert ball.projectile_speed_multiplier == 1.0
