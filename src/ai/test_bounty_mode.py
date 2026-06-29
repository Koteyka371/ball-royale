import pytest
from ai.game_modes import BountyMode

class MockBall:
    def __init__(self, ball_type="tank"):
        self.ball_type = ball_type
        self.alive = True
        self.team = "Unknown"
        self.is_bounty = False
        self.hp = 100
        self.max_hp = 100
        self.speed = 100
        self.damage = 10
        self.radius = 10

class MockWorld:
    def __init__(self):
        self.dead_balls = []

def test_bounty_mode_setup():
    mode = BountyMode()
    world = MockWorld()
    balls = [MockBall() for _ in range(4)]

    mode.setup(world, balls)

    red_team = [b for b in balls if b.team == "Red"]
    blue_team = [b for b in balls if b.team == "Blue"]

    assert len(red_team) == 2
    assert len(blue_team) == 2

    red_bounties = [b for b in red_team if b.is_bounty]
    blue_bounties = [b for b in blue_team if b.is_bounty]

    assert len(red_bounties) == 1
    assert len(blue_bounties) == 1

    assert not mode.bounty_claimed["Red"]
    assert not mode.bounty_claimed["Blue"]

def test_bounty_mode_tick_buff():
    mode = BountyMode()
    world = MockWorld()
    balls = [MockBall() for _ in range(4)]

    mode.setup(world, balls)

    red_team = [b for b in balls if b.team == "Red"]
    blue_team = [b for b in balls if b.team == "Blue"]

    # Identify blue's bounty and kill it
    blue_bounty = [b for b in blue_team if b.is_bounty][0]
    blue_bounty.alive = False

    mode.tick(world, balls)

    # Red should be buffed
    assert mode.bounty_claimed["Red"] == True
    assert mode.bounty_claimed["Blue"] == False

    for b in red_team:
        assert b.damage == 20
        assert b.speed == 180.0
        assert b.max_hp == 200
        assert b.hp == 200
        assert b.radius == 12.5

def test_bounty_mode_check_winner():
    mode = BountyMode()
    world = MockWorld()
    balls = [MockBall() for _ in range(4)]

    mode.setup(world, balls)

    assert mode.check_winner(world, balls) is None

    # Kill all blue team
    for b in balls:
        if b.team == "Blue":
            b.alive = False

    assert mode.check_winner(world, balls) == "Red"

    # Kill all red team
    for b in balls:
        if b.team == "Red":
            b.alive = False

    assert mode.check_winner(world, balls) == "Draw"
