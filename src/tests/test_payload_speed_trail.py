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
        self.speed_boost_timer = 0.0
        self.radius = 15.0

def test_escort_mode_speed_trail():
    world = MockWorld()
    mode = EscortMode()
    mode.pulse_timer = 5.0
    balls = [
        MockBall(x=100.0, y=500.0, team="Defenders"), # payload
        MockBall(x=150.0, y=500.0, team="Defenders"), # close teammate
        MockBall(x=150.0, y=500.0, team="Defenders"), # extra to avoid setup overwriting teams
        MockBall(x=500.0, y=500.0, team="Defenders"), # far teammate
        MockBall(x=900.0, y=500.0, team="Attackers"), # extra
        MockBall(x=900.0, y=500.0, team="Attackers"), # extra
        MockBall(x=900.0, y=500.0, team="Attackers"), # extra
        MockBall(x=900.0, y=500.0, team="Attackers"), # extra
    ]
    mode.setup(world, balls)
    mode.chosen_path = 0 # force deterministic path

    # Setup manually forces teams based on index, so fix them up explicitly
    balls[0].team = "Defenders"
    balls[1].team = "Defenders"
    balls[2].team = "Defenders"

    # Restore coords since setup moves the payload
    mode.payload.x = 100.0
    mode.payload.y = 500.0
    balls[1].x = 150.0
    balls[1].y = 500.0
    balls[2].x = 500.0
    balls[2].y = 500.0

    assert balls[1].speed_boost_timer == 0.0
    assert balls[2].speed_boost_timer == 0.0

    mode.tick(world, balls, 1.0)

    assert balls[1].speed_boost_timer == pytest.approx(2.0), "Close teammate should get a speed boost trail"
    assert balls[2].speed_boost_timer == 0.0, "Far teammate should not get a speed boost trail"


def test_dual_payload_mode_speed_trail():
    world = MockWorld()
    mode = DualPayloadMode()
    balls = [
        MockBall(x=100.0, y=500.0, team="Red"),      # red payload
        MockBall(x=850.0, y=500.0, team="Red"),      # close red pusher (for blue payload)
        MockBall(x=500.0, y=500.0, team="Red"),      # far red pusher
        MockBall(x=900.0, y=500.0, team="Blue"),     # blue payload
        MockBall(x=150.0, y=500.0, team="Blue"),     # close blue pusher (for red payload)
        MockBall(x=500.0, y=500.0, team="Blue")      # far blue pusher
    ]
    mode.setup(world, balls)

    # Fix teams that might have been changed by setup
    balls[0].team = "Red"
    balls[1].team = "Red"
    balls[2].team = "Red"
    balls[3].team = "Blue"
    balls[4].team = "Blue"
    balls[5].team = "Blue"

    # Restore coords
    mode.payload_red.x = 100.0
    mode.payload_red.y = 500.0
    balls[1].x = 850.0
    balls[1].y = 500.0
    balls[2].x = 500.0
    balls[2].y = 500.0

    mode.payload_blue.x = 900.0
    mode.payload_blue.y = 500.0
    balls[4].x = 150.0
    balls[4].y = 500.0
    balls[5].x = 500.0
    balls[5].y = 500.0

    mode.tick(world, balls, 1.0)

    assert balls[4].speed_boost_timer == pytest.approx(2.0), "Close blue pusher should get a speed boost trail"
    assert balls[5].speed_boost_timer == 0.0, "Far blue pusher should not get a speed boost trail"

    assert balls[1].speed_boost_timer == pytest.approx(2.0), "Close red pusher should get a speed boost trail"
    assert balls[2].speed_boost_timer == 0.0, "Far red pusher should not get a speed boost trail"

if __name__ == '__main__':
    pytest.main(["-v", __file__])
