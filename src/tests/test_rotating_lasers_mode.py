import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, team="Red"):
        self.id = id
        self.x = 500.0
        self.y = 500.0
        self.radius = 15.0
        self.alive = True
        self.team = team
        self.ball_type = "player"

def test_rotating_lasers_mode_spawn():
    world = MockWorld()
    mode = GAME_MODES.get("rotating_lasers")
    assert mode is not None

    balls = [MockBall(i) for i in range(2)]

    mode.setup(world, balls)
    mode.tick(world, balls, 1.0)

    assert len(world.arena.hazards) == 1

    h = world.arena.hazards[0]
    assert h.kind == "rotating_laser_wall"
    assert h.damage == 50.0
    assert h.radius == 1500.0
    assert h.rotation_speed == 0.5
    assert h.angle == 0.0
