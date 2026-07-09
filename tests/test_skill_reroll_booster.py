import pytest
from src.ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, radius=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.skill = "old_skill"
        self.SKILL = "old_skill"
        self.skill_timer = 5.0
        self.speed = 2.0

class MockEntity:
    def __init__(self, x=0, y=0, kind="booster", radius=10):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []

def test_skill_reroll_booster_collection():
    ball = MockBall(0, 0)
    world = MockWorld()
    world.balls.append(ball)

    booster = MockEntity(10, 0, kind="skill_reroll_booster")
    world.boosters.append(booster)
    world.arena.hazards.append(booster)

    action = Action(ball, world)
    # mock methods
    action._get_boosters = lambda: world.boosters
    action._get_enemies = lambda: []

    # act
    action.execute("collect_booster", 1.0)

    # assert
    assert len(world.boosters) == 0
    assert len(world.arena.hazards) == 0
    assert ball.skill != "old_skill"
    assert ball.SKILL != "old_skill"
    assert ball.skill == ball.SKILL
    assert ball.skill_timer == 0.0
