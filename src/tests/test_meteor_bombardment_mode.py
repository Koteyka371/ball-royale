import math
import pytest
from ai.game_modes import MeteorBombardmentMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.vx = 0.0
        self.vy = 0.0
        self.base_speed = 10.0
        self.speed = 10.0

    def take_damage(self, amount):
        self.hp -= amount

def test_meteor_bombardment_spawns_and_damages():
    mode = MeteorBombardmentMode()
    world = MockWorld()
    balls = [MockBall(1, 500, 500)]

    mode.setup(world, balls)

    # Trigger spawn
    mode.bombard_timer = 9.9
    mode.tick(world, balls, delta=0.2)
    assert len(mode.active_meteors) >= 5

    # Force a meteor to land directly on the ball
    mode.active_meteors = [{"id": "meteor_1", "x": 500, "y": 500, "delay": 0.1, "radius": 40.0}]

    # Tick to make it land (0.2s delta means it lands this frame)
    mode.tick(world, balls, delta=0.2)

    # Initial damage 50.0 + (20.0 * 0.2) from crater = 54.0 total damage
    # 100.0 - 54.0 = 46.0
    assert abs(balls[0].hp - 46.0) < 0.01

    # Assert crater creation
    assert len(mode.craters) == 1

    # Tick again for crater DOT (1.0s = 20 damage)
    mode.tick(world, balls, delta=1.0)

    # 46.0 - 20.0 = 26.0
    assert abs(balls[0].hp - 26.0) < 0.01

def test_meteor_bombardment_knockback():
    mode = MeteorBombardmentMode()
    world = MockWorld()
    balls = [MockBall(1, 510, 500)] # Slightly offset

    mode.setup(world, balls)

    # Trigger spawn
    mode.bombard_timer = 9.9
    mode.tick(world, balls, delta=0.2)

    mode.active_meteors = [{"id": "meteor_1", "x": 500, "y": 500, "delay": 0.1, "radius": 40.0}]

    mode.tick(world, balls, delta=0.2)

    # Assert knockback
    assert balls[0].vx > 0
    assert balls[0].vy == 0
