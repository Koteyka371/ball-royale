import pytest
from ai.game_modes import GAME_MODES, TickingPayloadMode

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

def test_ticking_payload_setup():
    mode = TickingPayloadMode()
    world = MockWorld()
    balls = [MockBall(ball_type="brawler"), MockBall(ball_type="sniper")]

    mode.setup(world, balls)

    assert len(balls) == 3 # Payload added
    payload = balls[2]
    assert payload.ball_type == "payload"
    assert payload.x == 500.0
    assert payload.y == 500.0
    assert payload.team == "Neutral"

    assert balls[0].team == "Red"
    assert balls[1].team == "Blue"

def test_ticking_payload_tick_movement():
    mode = TickingPayloadMode()
    world = MockWorld()
    # Red is at (400, 500) and Blue is at (900, 500), payload at (500, 500)
    # Distance to Red is 100, which is < 150. Red should push to the right.
    balls = [MockBall(ball_type="brawler", x=400.0, y=500.0), MockBall(ball_type="sniper", x=900.0, y=500.0)]
    mode.setup(world, balls)

    mode.tick(world, balls, 1.0)
    payload = mode.payload

    assert payload.x > 500.0 # Red pushes towards Blue goal (right)

def test_ticking_payload_explode_on_timer():
    mode = TickingPayloadMode()
    world = MockWorld()
    b1 = MockBall(ball_type="brawler", x=550.0, y=500.0) # within 200 radius
    b2 = MockBall(ball_type="sniper", x=800.0, y=500.0) # outside 200 radius
    balls = [b1, b2]
    mode.setup(world, balls)

    # Set timer to trigger explosion
    mode.timer = 0.0

    mode.tick(world, balls, 1.0)

    assert not mode.payload.alive
    assert mode.winner == "Draw"

    assert not b1.alive
    assert b1.hp == 0
    assert b1 in world.dead_balls

    assert b2.alive
    assert b2.hp == 100.0
    assert b2 not in world.dead_balls

def test_ticking_payload_reach_goal():
    mode = TickingPayloadMode()
    world = MockWorld()
    balls = [MockBall(ball_type="brawler", x=900.0, y=500.0)]
    mode.setup(world, balls)

    # Move payload to Blue base
    mode.payload.x = 950.0

    mode.tick(world, balls, 1.0)

    assert not mode.payload.alive
    assert mode.winner == "Red" # Red pushed it to Blue goal

    # Reset
    mode = TickingPayloadMode()
    mode.setup(world, balls)
    mode.payload.x = 50.0

    mode.tick(world, balls, 1.0)

    assert not mode.payload.alive
    assert mode.winner == "Blue" # Blue pushed it to Red goal
