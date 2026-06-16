import sys
import os
import math

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action

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

class MockEnemy:
    def __init__(self, x=10, y=0, radius=10, ball_type="enemy_ball", alive=True):
        self.x = x
        self.y = y
        self.radius = radius
        self.ball_type = ball_type
        self.alive = alive

class MockAlly:
    def __init__(self, x=10, y=0, radius=10, ball_type="mock_ball", alive=True):
        self.x = x
        self.y = y
        self.radius = radius
        self.ball_type = ball_type
        self.alive = alive

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.enemies = []
        self.allies = []

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": self.enemies,
            "allies": self.allies,
            "boosters": [],
            "traps": []
        }

def test_flee_safe_distance():
    # If the enemy is > perception_radius * 0.8, it should not move via flee logic (it enters _idle which moves slightly)
    ball = MockBall(x=500, y=500, speed=10)
    world = MockWorld()
    world.enemies = [MockEnemy(x=400, y=500)] # Distance 100 > 100 * 0.8 (80)
    action_layer = Action(ball, world)

    orig_x = ball.x
    action_layer.execute("flee", 0.1)

    # Idle moves slightly, but flee would move it explicitly by boosted_speed * delta * 60 (15 * 0.1 * 60 = 90)
    # So if it moved 90, it fled. If it moved < 10, it idled.
    assert abs(ball.x - orig_x) < 5
    assert ball.current_action == "flee"

def test_flee_speed_boost():
    # Enemy is close (distance 50)
    ball = MockBall(x=500, y=500, speed=10)
    world = MockWorld()
    world.enemies = [MockEnemy(x=450, y=500)]
    action_layer = Action(ball, world)

    action_layer.execute("flee", 0.1)

    # Should move away perfectly to the right since safe zone pull is 0 (we are at 500,500) and no allies
    # Distance moved should be speed * 1.5 * delta * 60 = 10 * 1.5 * 0.1 * 60 = 90
    assert math.isclose(ball.x, 590.0, rel_tol=1e-5)
    assert ball.y == 500

def test_flee_towards_ally():
    # Enemy is left (450, 500)
    # Ally is up (500, 450)
    # The flee vector goes right (1, 0)
    # The ally vector goes up (0, -1)
    # The combined vector before normalization is (1, -0.4)
    ball = MockBall(x=500, y=500, speed=10)
    world = MockWorld()
    world.enemies = [MockEnemy(x=450, y=500)]
    world.allies = [MockAlly(x=500, y=450)]
    action_layer = Action(ball, world)

    action_layer.execute("flee", 0.1)

    # Should move down-right
    assert ball.x > 500 # Moved right away from enemy
    assert ball.y < 500 # Moved up towards ally
