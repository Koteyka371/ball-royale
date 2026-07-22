import pytest
from ai.game_modes import TiltingPlatformMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, x, y):
        self.id = id(self)
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "player"
        self.hp = 100

def test_tilting_platform_center():
    mode = TiltingPlatformMode()
    world = MockWorld()
    b = MockBall(100, 100)
    mode.setup(world, [b])

    mode.tilt_direction = "center"

    old_dist = ((500 - b.x)**2 + (500 - b.y)**2)**0.5

    # Tick with large delta to see effect
    mode.tick(world, [b], delta=1.0)

    new_dist = ((500 - b.x)**2 + (500 - b.y)**2)**0.5

    assert new_dist < old_dist

def test_tilting_platform_edge():
    mode = TiltingPlatformMode()
    world = MockWorld()
    b = MockBall(100, 100)
    mode.setup(world, [b])

    mode.tilt_direction = "edge"

    old_dist = ((500 - b.x)**2 + (500 - b.y)**2)**0.5

    # Tick with large delta to see effect
    mode.tick(world, [b], delta=1.0)

    new_dist = ((500 - b.x)**2 + (500 - b.y)**2)**0.5

    assert new_dist > old_dist

def test_tilting_platform_switch():
    mode = TiltingPlatformMode()
    world = MockWorld()
    b = MockBall(100, 100)
    mode.setup(world, [b])

    mode.tilt_duration = 0.5
    mode.tilt_timer = 0.0
    mode.tick(world, [b], delta=0.6)

    assert mode.tilt_timer == 0.0
