import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action
from ai.decision import Decision

class MockBall:
    def __init__(self, x=0, y=0, speed=10, radius=10):
        self.current_action = None
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius
        self.perception_radius = 100
        self.skill_timer = 0.0
        self.ball_type = "mock_ball"
        self.alive = True
        self.used_skill = False
        self.damage = 20.0
        self.attack_timer = 0.0

    def use_skill(self):
        self.used_skill = True

class MockEnemy:
    def __init__(self, x=10, y=0, radius=10, ball_type="enemy_ball", alive=True, vx=0.0, vy=0.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.ball_type = ball_type
        self.alive = alive
        self.hp = 100.0
        self.max_hp = 100.0
        self.vx = vx
        self.vy = vy

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.enemies = []
        self.boosters = []
        self.dealt_damage = False
        self.collected_booster = False

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": self.enemies,
            "allies": [],
            "boosters": self.boosters,
            "traps": []
        }

    def _deal_damage(self, ball, target):
        self.dealt_damage = True

def test_decision_flank():
    ball = MockBall()
    ball.ball_type = "ninja"
    ball.personality = "ninja"
    world = MockWorld()
    world.enemies = [MockEnemy(x=100, y=100)]
    decision = Decision(ball, world)

    # Should get a high score for flank
    action = decision.choose_action({"danger_level": 0.0, "opportunity_level": 0.0, "threat_level": 0.0}, "idle")
    assert action == "flank"

def test_execute_flank_movement():
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    # Enemy is at (200, 100), moving right (vx=1.0)
    enemy = MockEnemy(x=200, y=100, vx=1.0, vy=0.0)
    world.enemies = [enemy]
    action_layer = Action(ball, world)

    action_layer.execute("flank", 0.1)

    # Target position should be behind the enemy. Since enemy moves right (vx=1.0),
    # target is to the left of the enemy: x = 200 - 1.0 * 20 = 180, y = 100.
    # Ball is at (100, 100), so it should move right (towards 180).
    assert ball.x > 100
    # Because of obstacle avoidance the exact path might vary, but generally moving right.

    # Test damage application
    ball2 = MockBall(x=180, y=100)
    world2 = MockWorld()
    enemy2 = MockEnemy(x=200, y=100, vx=1.0, vy=0.0)
    world2.enemies = [enemy2]
    action_layer2 = Action(ball2, world2)

    action_layer2.execute("flank", 0.1)
    assert world2.dealt_damage
    # Enemy HP should be reduced by 0.5 * damage = 0.5 * 20.0 = 10.0
    assert enemy2.hp == 90.0

if __name__ == "__main__":
    test_decision_flank()
    test_execute_flank_movement()
    print("Tests passed.")
