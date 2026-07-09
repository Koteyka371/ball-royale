import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action
import math

class MockBall:
    def __init__(self, color, level, x):
        self.alive = True
        self.hp = 100
        self.x = x
        self.y = 0
        self.radius = 10
        self.cosmetic_aura_color = color
        self.level = level
        self.id = 1
        self.ball_type = "warrior"

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.game_mode = None
        self.arena = type("Arena", (), {"hazards": []})
        self.tick = 0

    def get_nearby_entities(self, ball, radius):
        return [b for b in self.balls if b != ball]

def test_explosion():
    b1 = MockBall((1.0, 0.0, 0.0, 1.0), 10, 0)
    b2 = MockBall((0.0, 1.0, 0.0, 1.0), 10, 5)

    world = MockWorld([b1, b2])
    action = Action(b1, world)

    bounced = action._resolve_collisions()

    print(f"bounced1: {bounced}")
    print(f"b1 hp: {b1.hp}")
    print(f"b2 hp: {b2.hp}")

test_explosion()
print("Success")
