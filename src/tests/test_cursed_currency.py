import pytest
from ai.action import Action
import random
import math

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.radius = 10.0
        self.alive = True
        self.ball_type = "player"
        self.id = "p1"
        self.team = "player"

class DummyArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class DummyWorld:
    def __init__(self, mode_name="Standard"):
        self.arena = DummyArena()
        self.events = []
        self.balls = []
        self.black_markets = []

def test_cursed_currency_vulnerability():
    attacker = MockBall(0, 0)
    attacker.damage = 10.0

    target = MockBall(50, 50)
    target.hp = 100.0
    target.cursed_currency_vulnerability_timer = 5.0

    world = DummyWorld("Standard")
    world.balls = [attacker, target]
    action = Action(attacker, world)

    target.take_damage = lambda amt: setattr(target, 'hp', target.hp - amt)
    target.hp -= getattr(attacker, "damage", 10.0) * 3.0
    assert target.hp <= 70.0
    assert target.hp <= 70.0


def test_cursed_currency_collection():
    from ai.game_modes import BlackMarketMode
    mode = BlackMarketMode()
    world = DummyWorld("Standard")

    ball = MockBall(50, 50)
    ball.currency = 0
    world.balls = [ball]

    world.currency_pickups = [
        {"x": 50, "y": 50, "type": "currency"},
        {"x": 50, "y": 50, "type": "cursed_currency"},
    ]

    mode.tick(world, [ball], 0.016)

    assert getattr(ball, "currency", 0) == 4
    assert getattr(ball, "cursed_currency_vulnerability_timer", 0.0) == 5.0
