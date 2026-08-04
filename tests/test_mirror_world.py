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
        self.id = 1
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = "A"
        self.is_clone = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = [MockEntity(100, 100, 5, 5)]
        self.balls = []

def test_mirror_world_mode():
    mode = MirrorWorldMode()
    world = MockWorld()
    ball = MockEntity(250, 250, 2, 2)
    balls = [ball]
    world.balls = balls.copy()

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

    # Verify shadow was spawned and tracks owner
    assert len(world.balls) == 2
    shadow = mode.shadows[0]
    assert shadow.is_mirror_shadow
    assert shadow.owner == balls[0]

    # In mirror dimension, the real ball x=750. So the shadow should be at 500 + (500 - 750) = 250
    # Let's run an update tick to ensure position synchronizes
    mode.tick(world, balls, 0.016)
    assert shadow.x == 250

    # Test damage transfer
    shadow.hp -= 20.0
    mode.tick(world, balls, 0.016)
    assert balls[0].hp == 80.0
    assert shadow.hp == 80.0

    # Cross 5s mirror duration to revert
    mode.tick(world, balls, 5.0)
    assert not mode.is_mirrored
    assert balls[0].x == 250
    assert balls[0].vx == 2

    # Shadow should be removed from world
    assert len(world.balls) == 1
    assert len(mode.shadows) == 0
