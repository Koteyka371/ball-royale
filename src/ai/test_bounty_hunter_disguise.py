import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action
from ai.ball_types_bounty_hunter import BountyHunter

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.team = "blue"
        self.color = "blue"
        self.label = "Enemy"
        self.ball_type = "normal"
        self.vx = 0
        self.vy = 0
        self.speed = 100
        self.base_speed = 100
        self.is_bounty = True
        self.high_threat = False
        self.is_bounty_target = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = type('MockArena', (), {'hazards': []})
        self.boosters = []
        self.events = []
        self.tick = 0

def test_bh_indicator_disguised():
    world = MockWorld()
    bh = BountyHunter(1, 0, 0)
    bh.team = "red"
    bh.color = "orange"
    bh.label = "Bounty Hunter"
    bh.vx = 0
    bh.vy = 0
    bh.SKILL = "impostor_disguise"
    bh.skill = "impostor_disguise"

    normal = MockBall(2, 50, 50)

    world.balls.extend([bh, normal])

    action = Action(bh, world)

    # Tick 3 times to get indicator event (before disguise)
    for _ in range(3):
        action.execute('aggressive', 1.0)

    assert any(e.get("type") == "bounty_compass" for e in world.events)

    # Now disguise using the skill
    action._use_skill()

    assert getattr(bh, "is_disguised", False) is True
    assert getattr(bh, "color", "") == "blue"

    world.events = []

    for _ in range(3):
        action.execute('aggressive', 1.0)

    assert not any(e.get("type") == "bounty_compass" for e in world.events)

    # Tick until disguise ends
    for _ in range(6):
        action.execute('aggressive', 1.0)

    assert getattr(bh, "is_disguised", False) is False
    assert getattr(bh, "color", "") == "orange"
