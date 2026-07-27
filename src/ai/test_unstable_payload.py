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
        self.dead_balls = []

class MockBall:
    def __init__(self, team="Neutral", x=0, y=0, ball_type="basic"):
        self.team = team
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.alive = True
        self.speed = 10.0
        self.base_speed = 10.0
        self.max_hp = 100.0
        self.hp = 100.0

def test_unstable_payload_spawns():
    mode = GAME_MODES["unstable_payload"]
    mode.spawn_timer = 0.0
    mode.detonated = False
    world = MockWorld()
    balls = []

    mode.tick(world, balls, 1.0)
    assert len(balls) == 1
    assert balls[0].team == "Hazard"
    assert balls[0].radius == 20.0


def test_unstable_payload_expands_and_radiates():
    mode = GAME_MODES["unstable_payload"]
    mode.spawn_timer = 0.0
    mode.detonated = False
    mode.payload = None
    world = MockWorld()
    balls = [MockBall("Red", 550, 500)]

    mode.tick(world, balls, 1.0) # spawns
    assert len(balls) == 2

    mode.tick(world, balls, 1.0) # expands and damages
    payload = mode.payload
    assert payload.radius > 20.0
    assert balls[0].hp < 100.0

def test_unstable_payload_detonates():
    mode = GAME_MODES["unstable_payload"]
    mode.spawn_timer = 0.0
    mode.detonated = False
    mode.payload = None
    world = MockWorld()
    balls = [MockBall("Red", 600, 500)]

    mode.tick(world, balls, 1.0) # spawns
    payload = mode.payload
    payload.radius = 150.0 # Force critical mass

    mode.tick(world, balls, 1.0)
    assert mode.detonated
    assert not payload.alive
    assert balls[0].hp == 0
    assert not balls[0].alive
