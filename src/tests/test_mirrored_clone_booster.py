import pytest
import sys
import os

sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = type('Arena', (), {'hazards': []})()
        self.boosters = []
        self.next_id = 1000

    def get_nearby_entities(self, ball, radius):
        return {"boosters": self.boosters, "allies": [], "enemies": []}

class MockBall:
    def __init__(self, x=0, y=0, vx=0, vy=0):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.max_hp = 100
        self.hp = 100
        self.damage = 10
        self.speed = 2.0
        self.perception_radius = 200
        self.alive = True
        self.intangible = False
        self.team = 1
        self.ball_type = "default"

def test_mirrored_clone_booster():
    world = MockWorld()
    ball = MockBall(0, 0, 10, 0)
    world.balls.append(ball)

    booster = type('Booster', (), {'kind': 'mirrored_clone_booster', 'x': 0, 'y': 0, 'active': True})()
    world.boosters.append(booster)

    action = Action(ball, world)
    action._get_boosters = lambda: [booster]
    action._collect_booster(1.0)

    # Needs to spawn 2 clones, both intangible, lasting 5s, doing no damage
    assert len(world.balls) == 3

    clones = world.balls[1:]
    for c in clones:
        assert c.damage == 0
        assert getattr(c, "is_decoy", False) == True
        assert getattr(c, "is_mirrored_clone", False) == True
        assert getattr(c, "intangible", False) == True
        assert getattr(c, "decoy_timer", 0) == 5.0
        assert getattr(c, "owner_id", None) == 1

if __name__ == '__main__':
    pytest.main(['src/tests/test_mirrored_clone_booster.py'])
