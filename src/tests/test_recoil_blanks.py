import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.ai.action import Action
import math

class MockBall:
    def __init__(self, x=0, y=0, vx=10, vy=0, speed=10):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = speed
        self.hp = 100
        self.skill_timer = 0
        self.skill = "recoil_blanks"
        self.damage = 10
        self.SKILL_COOLDOWN = 3.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.events = []
        self.mode = None
        self.current_mode_name = None
        self.game_mode = None
    def add_event(self, name, data):
        self.events.append((name, data))

def test_recoil_blanks():
    b = MockBall(vx=10, vy=0)
    w = MockWorld()
    w.balls.append(b)

    a = Action(b, w)

    a._use_skill()

    # Initial vx=10, thrust = 10 * 5 = 50. vx -= 50 => -40
    assert b.vx == -40
    assert b.skill_timer == 3.0
