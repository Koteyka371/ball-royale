import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

class MockBall:
    def __init__(self, x=0, y=0, team="", ball_type="default"):
        self.id = id(self) % 100000
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.speed = 50.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0

    def take_damage(self, amount, source=None):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

def test_boss_escort_mode_setup():
    mode = GAME_MODES["boss_escort"]
    world = MockWorld()
    balls = [MockBall(x=500, y=500, team="Team A"), MockBall(x=600, y=500, team="Team B")]

    mode.setup(world, balls)

    assert len(mode.bosses) == 2
    assert mode.bosses[0].team == "Team A"
    assert mode.bosses[1].team == "Team B"

def test_boss_escort_mode_tick():
    mode = GAME_MODES["boss_escort"]
    world = MockWorld()
    balls = [MockBall(x=500, y=500, team="Team A"), MockBall(x=600, y=500, team="Team B")]

    mode.setup(world, balls)

    # move enemy ball near boss 1
    balls[0].x = mode.bosses[1].x + 10
    balls[0].y = mode.bosses[1].y

    # tick
    mode.tick(world, balls, delta=0.016)

    # attack cooldown should be applied, damage should be taken
    assert mode.bosses[1].attack_cooldown > 0
    assert balls[0].hp < 100.0
