from ai.action import Action
import pytest
import math

class MockBall:
    def __init__(self, stamina, max_stamina):
        self.stamina = stamina
        self.max_stamina = max_stamina
        self.infinite_stamina_timer = 0
        self.speed = 100.0
        self.base_speed = 100.0
        self.speed_boost_timer = 0.0
        self.x = 0
        self.y = 0
        self.radius = 10
        self.team = "test_team"
        self.id = 1
        self.ball_type = "test"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.items = []
        self.balls = []

    def get_nearby_entities(self, entity, radius):
        return {'items': self.items, 'enemies': [], 'allies': [], 'boosters': self.boosters}

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockItem:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius

def test_stamina_booster_speed_boost_not_max():
    ball = MockBall(50.0, 100.0)
    world = MockWorld()
    item = MockItem("stamina_booster", 5, 5, 10)
    world.items.append(item)
    world.boosters.append(item)
    world.arena.hazards.append(item)
    world.balls.append(ball)
    action = Action(ball, world)

    ball.x = 5
    ball.y = 5
    action._collect_booster(0.1)

    assert ball.stamina == 100.0
    assert ball.speed_boost_timer == 0.0

def test_stamina_booster_speed_boost_max():
    ball = MockBall(100.0, 100.0)
    world = MockWorld()
    item = MockItem("stamina_booster", 5, 5, 10)
    world.items.append(item)
    world.boosters.append(item)
    world.arena.hazards.append(item)
    world.balls.append(ball)
    action = Action(ball, world)

    ball.x = 5
    ball.y = 5
    action._collect_booster(0.1)

    assert ball.stamina == 100.0
    assert ball.speed_boost_timer == 3.0

def test_stamina_booster_speed_overdrive():
    world = MockWorld()
    ball = MockBall(100, 100)
    ball.stamina = 100
    ball.max_stamina = 100
    ball.speed_boost_timer = 2.0
    action = Action(ball, world)

    item = MockItem("stamina_booster", 5, 5, 10)
    world.boosters.append(item)

    action._idle = lambda d: None
    action._collect_booster(0.1)

    # speed boost gets 3s added (2.0 + 3.0 = 5.0) and overdrive triggers
    assert ball.speed_boost_timer == 5.0
    assert getattr(ball, "speed_overdrive_timer", 0.0) == 5.0
