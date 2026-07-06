import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action

class MockEntity:
    def __init__(self, x, y, ball_type="enemy", radius=10):
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.radius = radius

class MockBall:
    def __init__(self, x=50, y=50, speed=10, attack_range=150.0):
        self.x = x
        self.y = y
        self.speed = speed
        self.attack_range = attack_range
        self.skill_timer = 0.0
        self.attack_timer = 0.0
        self.skill_cooldown = 5.0
        self.ball_type = "sniper"
        self.alive = True
        self.used_skill_count = 0
        self.attacked_count = 0

    def use_skill(self):
        self.used_skill_count += 1

class MockWorld:
    def __init__(self):
        self.entities = []

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [e for e in self.entities if e.ball_type == "enemy"],
            "allies": [e for e in self.entities if e.ball_type == "ally"],
        }

    def _deal_damage(self, ball, target):
        ball.attacked_count += 1

def test_kite_maintain_distance():
    ball = MockBall(x=100, y=100, speed=10, attack_range=150.0)
    world = MockWorld()
    # Enemy is very close (distance 50) -> Ball should move away
    enemy = MockEntity(x=150, y=100, ball_type="enemy")
    world.entities = [enemy]

    action = Action(ball, world)
    action.execute("kite", 0.1)

    # Distance was 50, < attack_range * 0.8 (120). Should move away from enemy.
    # Moving away from x=150 -> x should decrease.
    assert ball.x < 100

def test_kite_attack_when_in_range():
    ball = MockBall(x=100, y=100, speed=10, attack_range=150.0)
    world = MockWorld()
    # Enemy is in range but not too close (distance 130)
    # attack_range * 0.8 = 120. So 120 < 130 < 150. Should hold position and attack.
    enemy = MockEntity(x=230, y=100, ball_type="enemy")
    world.entities = [enemy]

    action = Action(ball, world)
    action.execute("kite", 0.1)

    assert ball.attacked_count > 0

def test_kite_approach_when_far():
    ball = MockBall(x=100, y=100, speed=10, attack_range=150.0)
    world = MockWorld()
    # Enemy is out of range (distance 200)
    enemy = MockEntity(x=400, y=100, ball_type="enemy")
    world.entities = [enemy]

    action = Action(ball, world)
    action.execute("kite", 0.1)

    # Should move towards enemy. x should increase.
    assert ball.x > 90
    assert ball.attacked_count == 0
