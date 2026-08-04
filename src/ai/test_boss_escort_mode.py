import sys
import math

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append({'type': type, 'data': data})

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockBall:
    def __init__(self, team="Red", ball_type="normal"):
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.x = 200.0
        self.y = 500.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.vx = 0.0
        self.vy = 0.0

from ai.game_modes import BossEscortMode

def test_boss_escort_mode_mechanics():
    world = MockWorld()
    b1 = MockBall(team="Red")
    b2 = MockBall(team="Blue")
    b2.x = 800.0
    b2.y = 500.0
    balls = [b1, b2]

    mode = BossEscortMode()
    mode.setup(world, balls)
    mode.setup_done = True

    # Check setup
    assert mode.boss_red is not None
    assert mode.boss_blue is not None

    # Check that bosses have moved after tick
    initial_red_x = mode.boss_red.x
    initial_blue_x = mode.boss_blue.x
    mode.tick(world, balls, 0.016)

    assert mode.boss_red.x != initial_red_x
    assert mode.boss_blue.x != initial_blue_x

    # Let red boss attack b2
    b2.team = "Blue"
    b2.x = mode.boss_red.x + 10.0
    b2.y = mode.boss_red.y
    mode.boss_red.attack_cooldown = 0
    mode.tick(world, balls, 0.016)
    assert b2.hp < 100.0

    # Let red boss heal b1
    b1.team = "Red"
    b1.hp = 50.0
    b1.x = mode.boss_red.x + 10.0
    b1.y = mode.boss_red.y
    mode.boss_red.heal_cooldown = 0
    mode.tick(world, balls, 0.016)
    assert b1.hp > 50.0

def test_boss_escort_mode_win_conditions():
    world = MockWorld()
    b1 = MockBall(team="Red")
    b2 = MockBall(team="Blue")
    balls = [b1, b2]

    mode = BossEscortMode()
    mode.setup(world, balls)
    mode.setup_done = True

    # Initial state
    assert mode.check_winner(world, balls) is None

    # Red boss dies
    mode.boss_red.alive = False
    assert mode.check_winner(world, balls) == "Blue"

    # Both die
    mode.boss_blue.alive = False
    assert mode.check_winner(world, balls) == "Draw"

    # Reset
    mode.boss_red.alive = True
    mode.boss_blue.alive = True

    # Red boss reaches base
    mode.boss_red.x = mode.goal_blue[0]
    mode.boss_red.y = mode.goal_blue[1]
    assert mode.check_winner(world, balls) == "Red"
