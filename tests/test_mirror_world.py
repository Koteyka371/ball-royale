import pytest
from src.ai.mirror_world import MirrorWorldMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = [MockEntity(200, 500, 10, 0)]
        self.boosters = [MockEntity(800, 200, -5, 0)]

class MockEntity:
    def __init__(self, x, y, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = [MockEntity(100, 100, 5, 5)]

def test_mirror_world_mode():
    mode = MirrorWorldMode()
    world = MockWorld()
    balls = [MockEntity(250, 250, 2, 2)]

    # Initial normal state, tick 9.99s
    mode.tick(world, balls, 9.99)
    assert not mode.is_mirrored
    assert balls[0].x == 250

    # Cross 10s threshold
    mode.tick(world, balls, 0.02)
    assert mode.is_mirrored
    # 250 mirrored horizontally around 500 (1000/2) => 500 + (500 - 250) = 750
    assert balls[0].x == 750
    assert balls[0].vx == -2

    assert world.arena.hazards[0].x == 800
    assert world.arena.hazards[0].vx == -10

    assert world.arena.boosters[0].x == 200
    assert world.arena.boosters[0].vx == 5

    assert world.projectiles[0].x == 900
    assert world.projectiles[0].vx == -5

    # Cross 5s mirror duration to revert
    mode.tick(world, balls, 5.0)
    assert not mode.is_mirrored
    assert balls[0].x == 250
    assert balls[0].vx == 2
