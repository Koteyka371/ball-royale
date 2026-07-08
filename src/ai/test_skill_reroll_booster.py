import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.tick = 0
        self.items = []

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [], "allies": [], "hazards": [], "items": [], "boosters": self.boosters}

class MockEntity:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 10

class MockBall:
    def __init__(self, x, y, skill):
        self.x = x
        self.y = y
        self.skill = skill
        self.SKILL = skill
        self.active_skill = skill
        self.id = 1
        self.alive = True
        self.radius = 10
        self.team = "blue"
        self.max_hp = 100
        self.hp = 100
        self.speed = 10

def test_skill_reroll_booster_collection():
    world = MockWorld()
    ball = MockBall(100, 100, "dash")
    world.balls.append(ball)

    # Place a skill reroll booster exactly on the ball
    booster = MockEntity(100, 100, "skill_reroll_booster")
    world.boosters.append(booster)

    action = Action(ball, world)

    # Actually, we need to mock _get_boosters or something similar

    action._collect_booster(0.016)

    # Booster should be removed
    assert booster not in world.boosters

    # The skill should be changed to one of the possible skills
    possible_skills = ["dash", "shield", "heal", "teleport", "clone", "grapple", "stealth", "chain_lightning", "black_hole", "meteor"]
    assert ball.skill in possible_skills
    assert ball.SKILL in possible_skills
