import pytest
from ai.game_modes import GAME_MODES
from ai.test_action_advanced import MockWorld

class FakeBall:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.ball_type = "normal"
        self.alive = True
        self.radius = 20.0
        self.team = None

def test_reverse_tug_of_war():
    mode = GAME_MODES["reverse_tug_of_war"]
    world = MockWorld()

    red_ball1 = FakeBall(100, 100)
    red_ball2 = FakeBall(100, 100)
    blue_ball1 = FakeBall(900, 100)
    blue_ball2 = FakeBall(900, 100)

    balls = [red_ball1, red_ball2, blue_ball1, blue_ball2]

    mode.setup(world, balls)

    assert mode.payload is not None
    assert mode.payload.x == 500

    mode.tick(world, balls, 1.0)
    assert mode.payload.x == 500

    # Red players get close
    red_ball1.x = 490
    red_ball1.y = 500
    red_ball2.x = 495
    red_ball2.y = 500

    mode.tick(world, balls, 1.0)
    assert mode.payload.x < 500

    mode.payload.x = 500

    # Blue players get close, Red moves away
    blue_ball1.x = 510
    blue_ball1.y = 500
    blue_ball2.x = 510
    blue_ball2.y = 500

    red_ball1.x = 100
    red_ball1.y = 100
    red_ball2.x = 100
    red_ball2.y = 100

    mode.tick(world, balls, 1.0)
    assert mode.payload.x > 500
