import pytest
import math
from ai.action import Action
from ai.decision import Decision

class MockBall:
    def __init__(self, x=100, y=100, ball_type="sniper", personality="sniper", hp=100, max_hp=100, perception_radius=250, radius=10, speed=2.0, skill_timer=0.0):
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.personality = personality
        self.hp = hp
        self.max_hp = max_hp
        self.perception_radius = perception_radius
        self.radius = radius
        self.speed = speed
        self.skill_timer = skill_timer
        self.current_action = "idle"
        self.alive = True

    def get_hp_percent(self):
        if self.max_hp == 0:
            return 0.0
        return float(self.hp) / float(self.max_hp)

class MockEnemy:
    def __init__(self, x=100, y=0, ball_type="warrior", radius=10, alive=True):
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.radius = radius
        self.alive = alive

class MockWorld:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height
        self.damage_dealt = False
        self.entities = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [e for e in self.entities if isinstance(e, MockEnemy)]}

    def _deal_damage(self, attacker, target):
        self.damage_dealt = True

def test_decision_kite():
    ball = MockBall(personality="sniper")
    world = MockWorld()
    world.entities = [MockEnemy()]
    decision = Decision(ball, world)

    perception = {
        "danger_level": 0.0,
        "opportunity_level": 0.0,
        "threat_level": 0.0,
        "opportunity_score": 0.0,
        "enemies": [1],
        "boosters": [],
        "allies": []
    }

    action = decision.choose_action(perception, "neutral")
    assert action == "kite"

def test_action_kite_retreat():
    ball = MockBall(x=100, y=100, speed=1.0, perception_radius=250)
    world = MockWorld()
    # Enemy is very close (distance 50)
    # Optimal distance is perception_radius / 2 = 125
    # So the ball should move away from the enemy.
    enemy = MockEnemy(x=150, y=100)
    world.entities = [enemy]

    action = Action(ball, world)
    action.execute("kite", 1.0)

    assert ball.x < 100  # Should have moved away (left)
    assert ball.current_action == "kite"

def test_action_kite_chase():
    ball = MockBall(x=100, y=100, speed=1.0, perception_radius=250)
    world = MockWorld()
    # Enemy is far away (distance 200)
    # Optimal distance is perception_radius / 2 = 125
    # So the ball should move towards the enemy.
    enemy = MockEnemy(x=300, y=100)
    world.entities = [enemy]

    action = Action(ball, world)
    action.execute("kite", 1.0)

    assert ball.x > 100  # Should have moved towards (right)

def test_action_kite_deal_damage():
    ball = MockBall(x=100, y=100, speed=1.0, perception_radius=250, radius=10)
    world = MockWorld()
    # Optimal distance = 125. Enemy at 125 away.
    # Distance is exactly optimal.
    # Deal damage condition: dist <= optimal_dist + ball_radius + target_radius + 5
    # 125 <= 125 + 10 + 10 + 5 (150). So damage should be dealt.
    enemy = MockEnemy(x=225, y=100, radius=10)
    world.entities = [enemy]

    action = Action(ball, world)
    action.execute("kite", 1.0)

    assert world.damage_dealt == True
