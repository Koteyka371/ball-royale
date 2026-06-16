import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ai.action import Action
from ai.personality import Personality

class MockBall:
    def __init__(self, x=0, y=0, ball_type="tank"):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 2.0
        self.radius = 10.0
        self.perception_radius = 250.0
        self.skill_timer = 0.0
        self.skill_cooldown = 5.0
        self.used_skill = False
        self.emotion_state = "neutral"
        self.ball_type = ball_type
        self.difficulty = "medium"
        self.personality = Personality("tank")
        self.current_action = "idle"
        self.team_message = None

    def use_skill(self):
        self.used_skill = True

class MockEnemy:
    def __init__(self, x=10, y=0, radius=10, ball_type="enemy_ball", alive=True, hp=100):
        self.x = x
        self.y = y
        self.radius = radius
        self.ball_type = ball_type
        self.alive = alive
        self.hp = hp

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.enemies = []
        self.boosters = []
        self.dealt_damage = False
        self.collected_booster = False

    def get_nearby_entities(self, ball, radius):
        return {"enemies": self.enemies, "allies": []}

    def _deal_damage(self, attacker, target):
        self.dealt_damage = True

def test_target_strong_tank():
    ball = MockBall(x=50, y=50, ball_type="tank")
    world = MockWorld()

    # Close enemy with low HP
    enemy_weak = MockEnemy(x=70, y=50, hp=50)
    # Far enemy with high HP
    enemy_strong = MockEnemy(x=150, y=50, hp=200)

    world.enemies = [enemy_weak, enemy_strong]
    action_layer = Action(ball, world)

    action_layer.execute("attack", 0.1)

    # The tank should have moved towards the strong enemy, meaning its x should increase
    # but the distance to the strong enemy should be the primary driver.
    # We can check the vector directly, or just assert it moved right.
    assert ball.current_action == "attack"
    assert ball.x > 50

    # Let's verify by checking the exact target inside the method if possible,
    # or by noting that it moves towards (150, 50) instead of (70, 50).
    # Since both are on the x-axis to the right, it will move right regardless.
    # To be certain, let's place the strong enemy on the y-axis.

    ball2 = MockBall(x=50, y=50, ball_type="tank")
    world2 = MockWorld()
    enemy_weak2 = MockEnemy(x=70, y=50, hp=50)   # To the right
    enemy_strong2 = MockEnemy(x=50, y=150, hp=200) # To the bottom
    world2.enemies = [enemy_weak2, enemy_strong2]
    action_layer2 = Action(ball2, world2)

    action_layer2.execute("attack", 0.1)

    # Should move towards enemy_strong2 (y increases, x stays roughly same or slight repel)
    assert ball2.y > 50
    assert ball2.x <= 51 # Shouldn't move much to the right
