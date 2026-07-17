import pytest
import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.events = []
        self.next_id = 9000

    def get_nearby_entities(self, ball, radius):
        return {"allies": [], "boosters": self.boosters, "enemies": [b for b in self.balls if getattr(b, "team", None) != ball.team]}

    def _deal_damage(self, attacker, target):
        damage = getattr(attacker, "damage", 10.0)
        target.hp -= damage

class MockBall:
    def __init__(self, id, team="red", ball_type="warrior", x=10.0, y=10.0, hp=100.0, max_hp=100.0):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
        self.alive = True
        self.speed = 100.0
        self.base_speed = 100.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.radius = 10.0

def test_explosive_decoy_collision():
    world = MockWorld()
    b1 = MockBall(id=1, team="red", x=10.0, y=10.0)
    b1.is_decoy = True
    b1.decoy_type = "explosive"

    b2 = MockBall(id=2, team="blue", x=15.0, y=15.0)

    world.balls = [b1, b2]

    action = Action(b1, world)
    action._resolve_collisions()

    # b2 should have taken 50 damage
    assert b2.hp == 50.0

    # b1 (decoy) should be dead
    assert b1.hp == 0
    assert b1.alive == False
