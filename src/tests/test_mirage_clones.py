import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action
import math

class DummyBall:
    def __init__(self, bid, x, y, alive=True):
        self.id = bid
        self.x = x
        self.y = y
        self.alive = alive
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.ball_type = "test"
        self.team = "test_team"
        self.is_fake_clone = False

class DummyWorld:
    def __init__(self):
        self.events = []
        self.balls = []
    def add_event(self, name, data):
        self.events.append((name, data))
    def get_nearby_entities(self, ball, radius):
        return {"boosters": [], "hazards": [], "balls": []}

def test_mirage_passive_spawn():
    w = DummyWorld()
    b = DummyBall(1, 0, 0)
    b.ball_type = "mirage"
    w.balls.append(b)
    a = Action(b, w)

    # Simulate moving
    b.vx = 5.0
    b.vy = 5.0
    b.mirage_spawn_timer = 0.0

    a.execute("idle", 0.1)

    assert len(w.balls) > 1
    clone = [ball for ball in w.balls if ball != b][0]
    assert getattr(clone, "is_fake_clone", False) == True
    assert clone.hp == 1
    assert clone.damage == 0

def test_mirage_clone_on_hit():
    w = DummyWorld()
    attacker = DummyBall(2, 50, 50)
    clone = DummyBall(3, 50, 50)
    clone.is_fake_clone = True
    clone.hp = 1

    a = Action(attacker, w)
    a._attempt_damage(attacker, clone)

    assert clone.hp <= 0
    assert getattr(attacker, "is_blinded", False) == True
    assert getattr(attacker, "blindness_timer", 0.0) > 0.0
