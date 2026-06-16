import sys
import os

# Add src to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

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
        self.used_skill = False

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

def test_execute_attack_sniper_kiting():
    # Test kiting (moving away when too close)
    ball = MockBall(x=100, y=100)
    ball.ball_type = "sniper"
    ball.perception_radius = 200 # optimal_dist = 100
    world = MockWorld()
    world.enemies = [MockEnemy(x=150, y=100)] # Enemy is 50 units away (too close, < 100 - 15)
    action_layer = Action(ball, world)

    action_layer.execute("attack", 0.1)
    assert ball.current_action == "attack"
    assert ball.x < 100 # Should kite back to the left
    assert world.dealt_damage # Within optimal_dist + 5 (105), distance is 50

    # Test pursuing (moving towards when too far)
    ball2 = MockBall(x=100, y=100)
    ball2.ball_type = "sniper"
    ball2.perception_radius = 200 # optimal_dist = 100
    world2 = MockWorld()
    world2.enemies = [MockEnemy(x=250, y=100)] # Enemy is 150 units away (too far, > 100 + 15)
    action_layer2 = Action(ball2, world2)

    action_layer2.execute("attack", 0.1)
    assert ball2.x > 100 # Should move towards enemy
    assert not world2.dealt_damage # Outside optimal_dist + 5 (105), distance is 150

    # Test optimal distance (stand still)
    ball3 = MockBall(x=100, y=100)
    ball3.ball_type = "sniper"
    ball3.perception_radius = 200 # optimal_dist = 100
    world3 = MockWorld()
    world3.enemies = [MockEnemy(x=200, y=100)] # Enemy is 100 units away (perfect)
    action_layer3 = Action(ball3, world3)

    action_layer3.execute("attack", 0.1)
    assert ball3.x == 100 # Should stand still
    assert world3.dealt_damage # Within optimal_dist + 5 (105), distance is 100

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

    action_layer.execute("use skill", 0.1)
    assert ball.current_action == "use skill"
    assert ball.used_skill

def test_execute_idle_fallback():
    ball = MockBall()
    world = MockWorld()
    action_layer = Action(ball, world)

    action_layer.execute("unknown_strategy", 0.1)
    assert ball.current_action == "unknown_strategy"
