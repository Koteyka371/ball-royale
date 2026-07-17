import pytest
import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
        self.boosters = []

    def get_nearby_entities(self, ball, radius):
        return {'enemies': [b for b in self.balls if b != ball]}

class MockEntity:
    def __init__(self, id, x, y, team="red"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.ball_type = team
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.suspended_projectiles = []
        self.state_history = []
        self.alive = True
        self.inventory = []
        self.wall_stick_timer = 0.0
        self.is_stunned = False

def test_position_swap_item_logic():
    w = MockWorld()
    b1 = MockEntity(1, 10, 10, "red")
    b2 = MockEntity(2, 100, 100, "blue")
    w.balls = [b1, b2]

    b1.inventory.append("position_swap")

    a = Action(b1, w)
    a.execute("flee", 0.0)

    assert "position_swap" not in b1.inventory
    assert b1.x == 100
    assert b1.y == 100
    assert b2.x == 10
    assert b2.y == 10
    assert b2.hp < 100, "Minor damage not applied"
    assert getattr(b2, "slow_timer", 0) > 0, "Enemy not slowed (slow_timer missing or <= 0)"

if __name__ == "__main__":
    test_position_swap_item_logic()
