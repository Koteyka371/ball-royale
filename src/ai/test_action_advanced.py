import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ai.action import Action

class MockEntity:
    def __init__(self, x, y, radius=10, alive=True, ball_type="enemy"):
        self.x = x
        self.y = y
        self.radius = radius
        self.alive = alive
        self.ball_type = ball_type

class MockBall:
    def __init__(self, x=50, y=50, speed=10, radius=10):
        self.current_action = None
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius
        self.perception_radius = 250
        self.skill_timer = 0.0
        self.skill_cooldown = 5.0
        self.ball_type = "mock_ball"
        self.alive = True
        self.used_skill_count = 0
        self.personality = "idle"

    def use_skill(self):
        self.used_skill_count += 1

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.entities = []

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [e for e in self.entities if e.ball_type == "enemy"],
            "allies": [e for e in self.entities if e.ball_type == "ally"],
            "boosters": [e for e in self.entities if e.ball_type == "booster"]
        }

    def _deal_damage(self, ball, target):
        pass

def test_cooldown_logic():
    ball = MockBall()
    world = MockWorld()
    action = Action(ball, world)

    # First use
    ball.skill_timer = 0
    action.execute("use_skill", 0.1)
    assert ball.used_skill_count == 1
    assert ball.skill_timer > 0 # Should be set to cooldown (and slightly reduced by delta)

    # Second use immediately (should fail due to cooldown)
    old_timer = ball.skill_timer
    action.execute("use_skill", 0.1)
    assert ball.used_skill_count == 1 # Still 1
    assert ball.skill_timer < old_timer # Timer decrements

def test_obstacle_avoidance_attack():
    ball = MockBall(x=50, y=50)
    world = MockWorld()
    target = MockEntity(x=150, y=50, ball_type="enemy")
    obstacle = MockEntity(x=100, y=50, ball_type="enemy") # Directly between ball and target
    world.entities = [target, obstacle]

    action = Action(ball, world)

    # Base movement without obstacle would be purely +x
    # With obstacle, it should have a y-component to go around
    action.execute("attack", 0.1)

    # Check that y changed, indicating it tried to go around
    assert ball.x > 50
    # Floating point might be slightly off, but it should not be exactly 50 if avoidance works
    # Wait, the obstacle avoidance pushes away from the center. If exactly on line, it might not budge y.
    # Let's offset the obstacle slightly to see a clear avoidance vector

def test_obstacle_avoidance_offset():
    ball = MockBall(x=50, y=50)
    world = MockWorld()
    target = MockEntity(x=150, y=50, ball_type="enemy")
    obstacle = MockEntity(x=65, y=55, ball_type="ally") # Slightly off center
    world.entities = [target, obstacle]

    action = Action(ball, world)

    action.execute("attack", 0.1)

    assert ball.x > 50
    # It should be pushed in the -y direction away from the obstacle
    assert ball.y < 50
