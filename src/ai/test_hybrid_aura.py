import math
import random
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, level, aura_color):
        self.id = id
        self.x = x
        self.y = y
        self.level = level
        self.cosmetic_aura_color = aura_color
        self.vx = 0
        self.vy = 0
        self.hp = 100
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.damage = 10.0
        self.alive = True
        self.speed_boost_timer = 0.0
        self._base_speed_set = True
        self.team = "player"

class MockWorld:
    def __init__(self):
        self.events = []

    def get_nearby_entities(self, ball, radius):
        return [b for b in getattr(self, "balls", []) if b != ball]

def test_hybrid_aura_chance():
    world = MockWorld()
    b1 = MockBall(1, 0, 0, 15, (1.0, 0.0, 0.0, 1.0))
    b2 = MockBall(2, 5, 0, 15, (0.0, 0.0, 1.0, 1.0))
    b2.team = "enemy"
    world.balls = [b1, b2]
    action = Action(b1, world)

    orig_random = random.random
    random.random = lambda: 0.05

    try:
        action._resolve_collisions()
    finally:
        random.random = orig_random

    assert getattr(b1, "_hybrid_aura_timer", 0) > 0.0
    assert getattr(b2, "_hybrid_aura_timer", 0) > 0.0
    assert b1.cosmetic_aura_color == (0.5, 0.0, 0.5, 1.0)
    assert b1.speed == 150.0

    action.execute("base", 5.0)
    assert getattr(b1, "_hybrid_aura_timer", 0) == 0.0
    assert b1.cosmetic_aura_color == (1.0, 1.0, 0.0, 1.0)
    assert b1.damage == 10.0
