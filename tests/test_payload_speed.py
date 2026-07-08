import pytest
from ai.game_modes import EscortMode, DualPayloadMode

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
    def __init__(self, team="Neutral", x=0.0, y=0.0, ball_type="basic"):
        self.team = team
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.alive = True
        self.speed = 10.0
        self.base_speed = 10.0
        self.max_hp = 100.0
        self.hp = 100.0

def test_escort_mode_speed_mult():
    world = MockWorld()
    # Teammate close vs Teammate far
    mode_slow = EscortMode()
    # To bypass pulse timer logic we simulate multiple ticks or artificially set pulse timer
    mode_slow.pulse_timer = 5.0
    balls_slow = [
        MockBall(x=100.0, y=500.0, team="Defenders"), # payload (defenders[0])
        MockBall(x=500.0, y=500.0, team="Defenders")  # far teammate
    ]
    mode_slow.setup(world, balls_slow) # setup overrides x and y of payload!
    payload_slow = mode_slow.payload

    # We must set coordinates AFTER setup
    payload_slow.x = 100.0
    payload_slow.y = 500.0
    balls_slow[1].x = 500.0
    balls_slow[1].y = 500.0
    balls_slow[1].team = "Defenders"

    mode_fast = EscortMode()
    mode_fast.pulse_timer = 5.0
    balls_fast = [
        MockBall(x=100.0, y=500.0, team="Defenders"), # payload (defenders[0])
        MockBall(x=150.0, y=500.0, team="Defenders")  # close teammate
    ]
    mode_fast.setup(world, balls_fast)
    payload_fast = mode_fast.payload

    payload_fast.x = 100.0
    payload_fast.y = 500.0
    balls_fast[1].x = 150.0
    balls_fast[1].y = 500.0
    balls_fast[1].team = "Defenders"

    mode_slow.tick(world, balls_slow, 1.0)
    mode_fast.tick(world, balls_fast, 1.0)

    slow_dist = payload_slow.x - 100.0
    fast_dist = payload_fast.x - 100.0

    # speed is 0.5. At 1.0 delta, dx=800, dy=0.
    # We should have slow_dist = 0.5 * 1.0 = 0.5
    # Since payload.speed isn't multiplied by delta in original code: self.payload.x += (dx / dist) * base_speed * speed_mult
    # So slow_dist is just base_speed * speed_mult (0.5 * 1.0) = 0.5
    # fast_dist is 0.5 * 1.5 = 0.75

    assert fast_dist > slow_dist
    assert fast_dist == pytest.approx(slow_dist * 1.5)

def test_dual_payload_speed_mult():
    world = MockWorld()
    mode_slow = DualPayloadMode()
    balls_slow = [
        MockBall(x=100.0, y=500.0, team="Red"),
        MockBall(x=500.0, y=500.0, team="Red"), # far red teammate
        MockBall(x=900.0, y=500.0, team="Blue"),
        MockBall(x=500.0, y=500.0, team="Blue")  # far blue teammate
    ]
    mode_slow.setup(world, balls_slow)
    # Setup overwrites coordinates, fix them
    mode_slow.payload_red.x = 100.0
    mode_slow.payload_red.y = 500.0
    mode_slow.payload_blue.x = 900.0
    mode_slow.payload_blue.y = 500.0
    balls_slow[1].x = 500.0
    balls_slow[1].y = 500.0
    balls_slow[3].x = 500.0
    balls_slow[3].y = 500.0

    mode_slow.tick(world, balls_slow, 1.0)
    slow_dist_red = mode_slow.payload_red.x - 100.0
    slow_dist_blue = 900.0 - mode_slow.payload_blue.x

    mode_fast = DualPayloadMode()
    balls_fast = [
        MockBall(x=100.0, y=500.0, team="Red"),
        MockBall(x=150.0, y=500.0, team="Red"), # close red teammate
        MockBall(x=900.0, y=500.0, team="Blue"),
        MockBall(x=850.0, y=500.0, team="Blue")  # close blue teammate
    ]
    mode_fast.setup(world, balls_fast)
    # Fix coordinates after setup
    mode_fast.payload_red.x = 100.0
    mode_fast.payload_red.y = 500.0
    mode_fast.payload_blue.x = 900.0
    mode_fast.payload_blue.y = 500.0
    balls_fast[1].x = 150.0
    balls_fast[1].y = 500.0
    balls_fast[3].x = 850.0
    balls_fast[3].y = 500.0

    mode_fast.tick(world, balls_fast, 1.0)
    fast_dist_red = mode_fast.payload_red.x - 100.0
    fast_dist_blue = 900.0 - mode_fast.payload_blue.x

    assert fast_dist_red > slow_dist_red
    assert fast_dist_blue > slow_dist_blue
    assert fast_dist_red == pytest.approx(slow_dist_red * 1.5)
    assert fast_dist_blue == pytest.approx(slow_dist_blue * 1.5)

if __name__ == '__main__':
    pytest.main(["-v", __file__])
