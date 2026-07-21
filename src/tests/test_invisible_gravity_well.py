import pytest

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.next_id = 1

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 15.0
        self.alive = True
        self.ball_type = "basic"

def test_invisible_gravity_wells():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES["invisible_gravity_wells"]

    world = MockWorld()
    ball = MockBall(1, 100, 100)
    world.balls.append(ball)

    # Tick past spawn timer
    mode.tick(world, world.balls, 6.0)

    # Check if a hazard was added
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert getattr(hazard, "kind", "") == "invisible_gravity_well"

    hazard.x = 200.0
    hazard.y = 100.0
    hazard.radius = 200.0

    old_vx = ball.vx

    mode.tick(world, world.balls, 0.1)

    assert ball.vx > old_vx # Because hazard is at 200, ball is at 100

    # tick until expire
    hazard.duration = 0.1
    mode.tick(world, world.balls, 0.1)

    assert len(world.arena.hazards) == 0
