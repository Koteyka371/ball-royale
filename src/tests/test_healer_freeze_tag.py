import pytest
import sys
sys.path.append('src')
from ai.game_modes import HealerFreezeTagMode

class MockBall:
    def __init__(self, team="Red"):
        self.team = team
        self.ball_type = "normal"
        self.is_frozen = False
        self.is_healer = False
        self.alive = True
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.stun_timer = 0.0
        self.frozen_timer = 0.0
        self.vx = 0.0
        self.vy = 0.0

class MockWorld:
    def __init__(self):
        self.dead_balls = []

def test_healer_freeze_tag_setup():
    mode = HealerFreezeTagMode()
    world = MockWorld()
    balls = [MockBall() for _ in range(4)]

    mode.setup(world, balls)

    red_team = [b for b in balls if b.team == "Red"]
    blue_team = [b for b in balls if b.team == "Blue"]

    assert len(red_team) == 2
    assert len(blue_team) == 2

    # Check that exactly one healer is assigned per team
    assert sum(1 for b in red_team if b.is_healer) == 1
    assert sum(1 for b in blue_team if b.is_healer) == 1

    # Healer should be unfrozen, others frozen
    for b in red_team:
        if b.is_healer:
            assert b.is_frozen is False
        else:
            assert b.is_frozen is True

def test_healer_freeze_tag_unfreeze():
    mode = HealerFreezeTagMode()
    world = MockWorld()
    balls = [MockBall(), MockBall()]

    mode.setup(world, balls) # Should make them both Red team (len=2, mid=1)

    # Setup creates 1 Red, 1 Blue. Let's manually set them to be same team
    balls[0].team = "Red"
    balls[1].team = "Red"

    balls[0].is_healer = True
    balls[0].is_frozen = False
    balls[1].is_healer = False
    mode._freeze_ball(balls[1])

    assert balls[1].is_frozen is True

    # Collision
    balls[0].x = 0
    balls[0].y = 0
    balls[1].x = 10
    balls[1].y = 0

    mode.tick(world, balls)

    assert balls[1].is_frozen is False

def test_healer_freeze_tag_win_condition():
    mode = HealerFreezeTagMode()
    world = MockWorld()
    balls = [MockBall("Red"), MockBall("Red"), MockBall("Blue"), MockBall("Blue")]

    # All unfrozen (should result in draw as both teams have 0 frozen)
    winner = mode.check_winner(world, balls)
    assert winner == "Draw"

    # Red has 1 frozen, Blue has 0
    balls[0].is_frozen = True
    winner = mode.check_winner(world, balls)
    assert winner == "Blue"

    # Red has 1 frozen, Blue has 1 frozen
    balls[2].is_frozen = True
    winner = mode.check_winner(world, balls)
    assert winner is None
