import pytest
from ai.game_modes import GAME_MODES, ReverseDualPayloadMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

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
        self.is_payload = False

def test_reverse_dual_payload():
    mode = GAME_MODES["reverse_dual_payload"]
    assert isinstance(mode, ReverseDualPayloadMode)
    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]
    mode.setup(world, balls)

    # Red payload starts near Blue side
    assert mode.payload_red.x == 900.0
    # Blue payload starts near Red side
    assert mode.payload_blue.x == 100.0

    # Red players are 0,1. Blue players are 2,3.
    # Put Red player 0 near Blue payload (100) -> push it right
    balls[0].x = 100.0
    balls[0].y = 500.0

    # Put Blue player 2 near Blue payload -> take damage
    balls[2].x = 100.0
    balls[2].y = 500.0

    mode.tick(world, balls, 1.0)

    # Blue payload should move right
    assert mode.payload_blue.x > 100.0

    # Blue player 2 should take damage (started at 100 hp, should be 85)
    assert balls[2].hp == 85.0
    # Red player 0 should not take damage
    assert balls[0].hp == 100.0
