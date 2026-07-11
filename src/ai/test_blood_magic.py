import pytest
from ai.action import Action

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards or []

class MockWorld:
    def __init__(self, arena, balls, boosters=None):
        self.arena = arena
        self.balls = balls
        self.boosters = boosters or []
        self.events = []

    def get_nearby_entities(self, ball, radius):
        return {"hazards": self.arena.hazards, "boosters": self.boosters, "enemies": [b for b in self.balls if b != ball]}

class MockBall:
    def __init__(self, id, x, y, hp=100, team="red", skill_timer=0):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.team = team
        self.skill_timer = skill_timer
        self.alive = True
        self.radius = 10
        self.speed = 0

    def take_damage(self, amount):
        self.hp -= amount

class MockHazard:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 10

def test_blood_magic_booster_pickup():
    arena = MockArena()
    ball = MockBall(1, 0, 0)
    booster = MockHazard(0, 0, "blood_magic_booster")
    arena.hazards.append(booster)
    world = MockWorld(arena, [ball], boosters=[booster])

    action = Action(ball, world)

    # Fake perception to see booster
    def mock_get_nearby_entities(radius, ignore_enemies=False):
        return {"hazards": arena.hazards, "boosters": world.boosters, "enemies": []}
    action._get_nearby_entities = mock_get_nearby_entities

    action.execute("collect_booster", 1.0)

    assert getattr(ball, "blood_magic_timer", 0) > 0
    assert booster not in arena.hazards
    assert booster not in world.boosters


def test_blood_magic_skill_cost():
    arena = MockArena()
    ball = MockBall(1, 0, 0, hp=100)
    ball.blood_magic_timer = 10.0
    ball._prev_skill_timer = 0.0
    world = MockWorld(arena, [ball])

    action = Action(ball, world)

    # Simulate skill usage
    ball.skill_timer = 5.0
    action._update_skill_timer(1.0)

    assert ball.hp == 90.0
    assert ball.skill_timer == 0.0
    assert ball._prev_skill_timer == 0.0
    assert len(world.events) == 1
    assert world.events[0]['data']['type'] == 'blood_magic_cast'


def test_blood_magic_micro_stun():
    import random
    arena = MockArena()
    attacker = MockBall(1, 0, 0)
    target = MockBall(2, 50, 0)

    attacker.blood_magic_timer = 10.0
    world = MockWorld(arena, [attacker, target])
    action = Action(attacker, world)

    random.seed(42) # Force predictable outcome if necessary, or mock random
    # Actually, random is heavily used. We'll patch random.random
    original_random = random.random
    random.random = lambda: 0.1 # < 0.2

    action._attempt_damage(attacker, target)

    random.random = original_random

    assert getattr(target, "stun_timer", 0) > 0
