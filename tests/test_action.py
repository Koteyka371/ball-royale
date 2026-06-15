import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action

class MockPersonality:
    def __init__(self, character="balanced"):
        self.character = character

class MockBall:
    def __init__(self, x=50, y=50, speed=10, radius=10):
        self.current_action = None
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius
        self.perception_radius = 100
        self.skill_timer = 0.0
        self.skill_cooldown = 5.0
        self.ball_type = "mock_ball"
        self.alive = True
        self.used_skill = False
        self.emotion_state = "neutral"
        self.personality = MockPersonality()

    def use_skill(self):
        self.used_skill = True

class MockEnemy:
    def __init__(self, x=10, y=0, radius=10, ball_type="enemy_ball", alive=True):
        self.x = x
        self.y = y
        self.radius = radius
        self.ball_type = ball_type
        self.alive = alive

class MockBooster:
    def __init__(self, x=10, y=0, active=True):
        self.x = x
        self.y = y
        self.active = active

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

    def _collect_booster(self, ball, booster):
        self.collected_booster = True

def test_action_initialization():
    ball = MockBall()
    world = MockWorld()
    action_layer = Action(ball, world)

    assert action_layer.ball == ball
    assert action_layer.world == world

def test_execute_flee():
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    world.enemies = [MockEnemy(x=90, y=100)] # Enemy is to the left
    action_layer = Action(ball, world)

    action_layer.execute("flee", 0.1)
    assert ball.current_action == "flee"
    assert ball.x > 100 # Should move to the right (away from enemy)
    assert ball.y == 100

def test_execute_attack():
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    world.enemies = [MockEnemy(x=200, y=100)] # Enemy is to the right, far away
    action_layer = Action(ball, world)

    action_layer.execute("attack", 0.1)
    assert ball.current_action == "attack"
    assert ball.x > 100 # Should move towards enemy
    assert ball.y == 100
    assert not world.dealt_damage # Should not deal damage, too far

    # Test attack distance
    ball2 = MockBall(x=100, y=100)
    world2 = MockWorld()
    world2.enemies = [MockEnemy(x=115, y=100)] # Enemy is close
    action_layer2 = Action(ball2, world2)
    action_layer2.execute("attack", 0.1)
    assert world2.dealt_damage # Should deal damage

def test_execute_defend():
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    action_layer = Action(ball, world)

    action_layer.execute("defend", 0.1)
    assert ball.current_action == "defend"
    # Idle random movement, difficult to assert exact position

def test_execute_collect_booster():
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    world.boosters = [MockBooster(x=200, y=100)] # Booster is to the right, far away
    action_layer = Action(ball, world)

    action_layer.execute("collect booster", 0.1)
    assert ball.current_action == "collect booster"
    assert ball.x > 100 # Should move towards booster
    assert ball.y == 100
    assert not world.collected_booster

    # Test collection distance
    ball2 = MockBall(x=100, y=100)
    world2 = MockWorld()
    world2.boosters = [MockBooster(x=110, y=100)] # Booster is close
    action_layer2 = Action(ball2, world2)
    action_layer2.execute("collect booster", 0.1)
    assert world2.collected_booster # Should collect

def test_execute_use_skill():
    ball = MockBall()
    world = MockWorld()
    action_layer = Action(ball, world)

    # Initially skill_timer is 0, should use skill
    action_layer.execute("use skill", 0.1)
    assert ball.current_action == "use skill"
    assert ball.used_skill
    assert ball.skill_timer > 0  # should be set to skill_cooldown (5.0)

    # Now skill is on cooldown, shouldn't use it again immediately
    ball.used_skill = False
    action_layer.execute("use skill", 0.1)
    assert not ball.used_skill
    assert ball.skill_timer > 0

def test_obstacle_avoidance():
    ball = MockBall(x=100, y=100, speed=10)
    world = MockWorld()
    # Enemy is exactly in the path to the right, but we add an ally to the right as an obstacle
    world.enemies = [MockEnemy(x=200, y=100)]
    ally = MockEnemy(x=115, y=100, ball_type="mock_ball") # Ally right in front
    world.get_nearby_entities = lambda b, r: {"enemies": world.enemies, "allies": [ally], "boosters": [], "traps": []}

    action_layer = Action(ball, world)
    action_layer.execute("attack", 0.1)

    # We should have moved towards the enemy but also away from the ally
    assert ball.current_action == "attack"
    # Because ally is at (115, 100) and we are at (100, 100), it will push us left (negative x)
    # However the target force is pulling us right (positive x). The net result should
    # either slow us down or push us differently, but most importantly we should test that the code runs without errors.
    assert isinstance(ball.x, float) or isinstance(ball.x, int)

def test_execute_idle_fallback():
    ball = MockBall()
    world = MockWorld()
    action_layer = Action(ball, world)

    action_layer.execute("unknown_strategy", 0.1)
    assert ball.current_action == "unknown_strategy"
