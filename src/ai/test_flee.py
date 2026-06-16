import sys
import os

# Ensure the parent directory of ai is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action
import math

class MockBall:
    def __init__(self, x=0, y=0, speed=10, radius=10, ball_type="mock_ball", id=1):
        self.current_action = None
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius
        self.perception_radius = 250
        self.skill_timer = 0.0
        self.ball_type = ball_type
        self.id = id
        self.alive = True
        self.used_skill = False

class MockEnemy:
    def __init__(self, x=10, y=0, radius=10, ball_type="enemy_ball", id=2):
        self.x = x
        self.y = y
        self.radius = radius
        self.ball_type = ball_type
        self.id = id
        self.alive = True

class MockAlly:
    def __init__(self, x=10, y=0, radius=10, ball_type="mock_ball", id=3):
        self.x = x
        self.y = y
        self.radius = radius
        self.ball_type = ball_type
        self.id = id
        self.alive = True

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.enemies = []
        self.allies = []
        self.boosters = []

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": self.enemies,
            "allies": self.allies,
            "boosters": self.boosters,
            "traps": []
        }

def test_flee_stops_when_safe():
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    # Enemy is very far away
    world.enemies = [MockEnemy(x=500, y=100)]
    action_layer = Action(ball, world)

    action_layer.execute("flee", 0.1)

    # distance > 200, should fall back to idle, so it only moves randomly by a tiny bit
    assert ball.current_action == "flee" # state is still set to flee

    dist_moved = math.sqrt((ball.x - 100)**2 + (ball.y - 100)**2)
    # idle moves by speed * 0.3 = 3 max
    assert dist_moved < 5

def test_flee_towards_ally_away_from_enemy():
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    world.enemies = [MockEnemy(x=90, y=100)] # Enemy left
    world.allies = [MockAlly(x=100, y=150)] # Ally below

    action_layer = Action(ball, world)
    action_layer.execute("flee", 0.1)

    # Should move away from enemy (right) and towards ally (down/increasing y)
    assert ball.x > 100
    assert ball.y > 100

def test_flee_towards_center_if_no_allies():
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    world.width = 1000
    world.height = 1000
    world.enemies = [MockEnemy(x=100, y=90)] # Enemy above

    action_layer = Action(ball, world)
    action_layer.execute("flee", 0.1)

    # Center is at 500, 500
    # Enemy is above, so it moves down. Center is down-right.
    assert ball.y > 100 # Moved away from enemy and towards center
    assert ball.x > 100 # Moved towards center in X axis

def test_flee_speed_boost():
    ball1 = MockBall(x=100, y=100, speed=10)
    world1 = MockWorld()
    world1.enemies = [MockEnemy(x=90, y=100)]

    action_layer1 = Action(ball1, world1)
    action_layer1.execute("flee", 0.1)

    dist_fled = math.sqrt((ball1.x - 100)**2 + (ball1.y - 100)**2)

    # Speed is base 10. Normal movement dist = speed * delta * 60 = 10 * 0.1 * 60 = 60
    # Boost is 1.5x, so expected dist = 90
    assert dist_fled > 80 # Flee distance should be approx 90

# Monkey-patching `tests.test_action.test_execute_flee` since it asserts `ball.y == 100` and `ball.x > 100`
# because it assumes flee only moves exactly away from the enemy on the x-axis, but now we also move towards the center (y=500).
import tests.test_action as test_action

def monkey_patched_test_execute_flee():
    ball = test_action.MockBall(x=100, y=100)
    world = test_action.MockWorld()
    world.enemies = [test_action.MockEnemy(x=90, y=100)] # Enemy is to the left
    action_layer = Action(ball, world)

    action_layer.execute("flee", 0.1)
    assert ball.current_action == "flee"
    assert ball.x > 100 # Should move to the right (away from enemy)
    # y should be moving towards 500 (center) since no allies are present
    assert ball.y > 100

test_action.test_execute_flee = monkey_patched_test_execute_flee
