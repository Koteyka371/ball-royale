import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True
        self.id = "p1"

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, kind, data):
        self.events.append((kind, data))

def test_inversion_field_mode():
    mode = GAME_MODES["inversion_field"]
    assert mode.name == "Inversion Field"

    world = MockWorld()

    # Simulate a ball that has just moved based on its velocity
    # e.g. started at (10, 10) with vx=100, vy=0
    # delta = 0.1s -> dx = 10 -> current pos = (20, 10)
    ball = MockBall(20.0, 10.0, 100.0, 0.0)
    balls = [ball]

    # Tick mode until interval reached (15.0 seconds)
    mode.tick(world, balls, delta=14.9)
    assert len(world.arena.hazards) == 0

    # Tick to cross interval, should spawn hazard immediately
    mode.tick(world, balls, delta=0.1) # reaches 15.0 exactly
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "inversion_field"
    assert hazard.duration == 7.9

    # Manually move hazard to overlap ball
    hazard.x = ball.x
    hazard.y = ball.y

    # Reset ball to know state
    ball.x = 20.0
    ball.y = 10.0
    ball.vx = 100.0
    ball.vy = 0.0

    # The tick should apply the reverse action for delta=0.1 because ball is in hazard.
    # ball.x was 20.0, vx is 100.0, delta is 0.1
    # bx -= 100.0 * 0.1 * 2 = 20.0
    # so ball.x becomes 0.0
    mode.tick(world, balls, delta=0.1)

    assert ball.x == 0.0
    assert ball.y == 10.0

    # Tick until duration (8.0 seconds) ends
    mode.tick(world, balls, delta=7.7)
    assert len(world.arena.hazards) == 1

    # Tick to cross duration
    mode.tick(world, balls, delta=0.2) # > 8.0
    assert len(world.arena.hazards) == 0
