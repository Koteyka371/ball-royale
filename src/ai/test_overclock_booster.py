import pytest
from ai.action import Action
import math

class MockBall:
    def __init__(self, x, y, team=1):
        self.x = x
        self.y = y
        self.team = team
        self.inventory = []
        self.skill_timer = 5.0
        self.speed = 100.0
        self.radius = 10.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.ball_type = "test"

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.events = []
        self.arena = MockArena()

    def get_nearby_entities(self, ball, radius):
        return {
            "boosters": self.boosters,
            "hazards": self.arena.hazards,
            "enemies": [b for b in self.balls if b != ball and b.team != ball.team],
            "allies": [b for b in self.balls if b != ball and b.team == ball.team],
            "items": []
        }

def test_overclock_booster_collect():
    ball1 = MockBall(0, 0, 1)
    ball1.skill_timer = 5.0

    ball2 = MockBall(50, 0, 1) # Ally, within range
    ball2.skill_timer = 10.0

    ball3 = MockBall(500, 0, 1) # Ally, out of range
    ball3.skill_timer = 10.0

    ball4 = MockBall(0, 50, 2) # Enemy, within range
    ball4.skill_timer = 10.0

    booster = MockBooster(0, 0, "overclock_booster")

    world = MockWorld()
    world.balls = [ball1, ball2, ball3, ball4]
    world.boosters = [booster]

    action = Action(ball1, world)
    # Collect booster first
    action._collect_booster(0.1)

    # Check booster was collected
    assert "overclock_booster" in ball1.inventory
    assert getattr(ball1, "overclock_timer", 0) == 5.0

    # Check cooldown reduction on nearby ally
    assert "overclock_booster" in ball2.inventory
    assert getattr(ball2, "overclock_timer", 0) == 5.0

    # Check out of range ally
    assert "overclock_booster" not in ball3.inventory

    # Check enemy
    assert "overclock_booster" not in ball4.inventory

    # Decay skill timers
    action.execute("flee", 1.0)
    assert ball1.skill_timer <= 5.0 - (1.0 * 10.0) # Reduces very fast

    action2 = Action(ball2, world)
    action2.execute("flee", 1.0)
    assert ball2.skill_timer <= 10.0 - (1.0 * 10.0) # Reduces very fast

def test_overclock_booster_timer():
    ball1 = MockBall(0, 0, 1)
    ball1.inventory = ["overclock_booster"]
    ball1.overclock_timer = 0.05

    world = MockWorld()
    world.balls = [ball1]

    action = Action(ball1, world)
    action.execute("flee", 0.1)

    # Timer should expire, removing item from inventory
    assert getattr(ball1, "overclock_timer", 0) == 0.0
    assert "overclock_booster" not in ball1.inventory
