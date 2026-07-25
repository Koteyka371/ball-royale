import pytest
from ai.action import Action
from ai.ball_types_trickster import Trickster

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.tick_timer = 1.0
        self.next_id = 1000

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 0
        self.y = 0
        self.ball_type = "trickster"
        self.skill = "trickster_smoke_bomb"
        self.skill_timer = 0
        self.hp = 100
        self.alive = True

def test_smoke_bomb():
    world = MockWorld()
    ball = MockBall()
    world.balls = [ball]
    action = Action(ball, world)

    action._use_skill()

    hazards = world.arena.hazards
    assert any(h.kind == "smoke_bomb" or h.kind == "smokescreen" or h.kind == "smoke_zone" for h in hazards)
