import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []

    def get_nearby_entities(self, ball, dist):
        return {"enemies": [b for b in self.balls if b != ball], "allies": []}

class MockArena:
    def __init__(self):
        self.hazards = []

class MockBall:
    def __init__(self, id, x, y, team="A"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.radius = 10.0
        self.perception_radius = 250.0
        self.speed = 2.0
        self.damage = 10.0
        self.ball_type = "test"
        self.badges = []
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.mass = 1.0

def test_cursed_relic_hot_potato_transfer():
    world = MockWorld()

    ball1 = MockBall(1, 0, 0, team="A")
    ball2 = MockBall(2, 5, 5, team="B")

    world.balls = [ball1, ball2]

    ball1.perception_radius = 25.0
    ball1.speed = 6.0
    ball1.damage = 30.0
    ball1.cursed_relic_timer = 5.0
    ball1.cursed_relic_applied = True

    action1 = Action(ball1, world)
    action1._resolve_collisions()

    assert getattr(ball1, 'cursed_relic_timer', 0.0) == 0.0
    assert getattr(ball2, 'cursed_relic_timer', 0.0) == 5.0
    assert getattr(ball2, 'cursed_relic_cooldown', 0.0) == 1.0

    # Ensure ball2 cannot immediately transfer it back to ball1
    action2 = Action(ball2, world)
    action2._resolve_collisions()

    assert getattr(ball2, 'cursed_relic_timer', 0.0) == 5.0
    assert getattr(ball1, 'cursed_relic_timer', 0.0) == 0.0

    assert getattr(ball1, 'cursed_relic_applied', False) == False
    assert getattr(ball2, 'cursed_relic_applied', False) == True

    # Check stats correctly restored for ball1
    assert ball1.perception_radius == 250.0
    assert ball1.speed == 2.0
    assert ball1.damage == 10.0

    # Check stats correctly modified for ball2
    assert ball2.perception_radius == 25.0
    assert ball2.speed == 6.0
    assert ball2.damage == 30.0
