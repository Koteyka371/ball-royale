import pytest
from ai.game_modes import MassivePinballArenaMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.events = []

    def add_event(self, type, payload):
        self.events.append((type, payload))

class MockBall:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = 10.0
        self.vy = 0.0
        self.speed = 100.0
        self.alive = True

def test_massive_pinball_arena_mode_setup():
    mode = MassivePinballArenaMode()
    world = MockWorld()
    balls = [MockBall(500, 500, 20)]

    mode.setup(world, balls)

    assert len(world.arena.hazards) == 8
    assert len(world.boosters) == 8
    assert all(getattr(h, "kind", "") == "massive_bumper" for h in world.arena.hazards)

def test_massive_pinball_arena_mode_tick_collision():
    mode = MassivePinballArenaMode()
    world = MockWorld()
    ball = MockBall(500, 500, 20)
    balls = [ball]

    mode.setup(world, balls)

    # Place a bumper exactly at (550, 500), radius 80
    # Ball is at 500, 500, radius 20
    # Distance is 50. Min dist is 100. They overlap.
    h = world.arena.hazards[0]
    h.x = 550
    h.y = 500
    h.radius = 80

    # Run tick
    mode.tick(world, balls, 0.1)

    # Ball should be pushed back and velocity updated
    assert ball.x < 500 # Ball is at 500, bumper at 550, nx is -50/50 = -1. Overlap is 50. x = 500 + (-1 * 50) = 450.

    # Speed is updated
    mag = (ball.vx**2 + ball.vy**2)**0.5
    assert mag > 100.0
