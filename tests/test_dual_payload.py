import pytest
from ai.game_modes import GAME_MODES, DualPayloadMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []
        self.items = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, id, ball_type="tank"):
        self.id = id
        self.ball_type = ball_type
        self.team = "solo"
        self.x = 500.0
        self.y = 500.0
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.speed = 100.0
        self.damage = 10.0

def test_dual_payload_setup():
    mode = GAME_MODES["dual_payload"]
    assert isinstance(mode, DualPayloadMode)

    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]

    mode.setup(world, balls)

    assert mode.payload_red is not None
    assert mode.payload_blue is not None

    assert mode.payload_red.ball_type == "payload"
    assert mode.payload_blue.ball_type == "payload"

    assert mode.payload_red.team == "Red"
    assert mode.payload_blue.team == "Blue"

    assert mode.payload_red.x == 100.0
    assert mode.payload_blue.x == 900.0

    assert mode.payload_red.hp == 500.0
    assert mode.payload_blue.hp == 500.0

def test_dual_payload_tick():
    mode = GAME_MODES["dual_payload"]
    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]

    mode.setup(world, balls)

    initial_red_x = mode.payload_red.x
    initial_blue_x = mode.payload_blue.x

    mode.tick(world, balls, 1.0)

    assert mode.payload_red.x > initial_red_x
    assert mode.payload_blue.x < initial_blue_x

def test_dual_payload_check_winner():
    mode = GAME_MODES["dual_payload"]
    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]

    mode.setup(world, balls)

    assert mode.check_winner(world, balls) is None

    mode.payload_red.alive = False
    assert mode.check_winner(world, balls) == "Blue"

    mode.payload_red.alive = True
    mode.payload_blue.alive = False
    assert mode.check_winner(world, balls) == "Red"

    mode.payload_red.alive = False
    mode.payload_blue.alive = False
    assert mode.check_winner(world, balls) == "Draw"
