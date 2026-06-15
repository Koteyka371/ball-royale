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
        self.skill_cooldown = 5.0
        self.attack_timer = 0.0
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

def test_attack_respects_cooldown():
    ball = MockBall(x=100, y=100)
    ball.attack_timer = 0.5 # Cooldown active
    world = MockWorld()
    world.enemies = [MockEnemy(x=115, y=100)] # Enemy is close
    action_layer = Action(ball, world)

    action_layer.execute("attack", 0.1)
    assert not world.dealt_damage # Should NOT deal damage
    assert ball.attack_timer == 0.4 # Cooldown should decrease

def test_attack_timing_by_type():
    ball_scout = MockBall(x=100, y=100)
    ball_scout.ball_type = "scout"
    world_scout = MockWorld()
    world_scout.enemies = [MockEnemy(x=115, y=100)]
    Action(ball_scout, world_scout).execute("attack", 0.0) # 0 delta to avoid subtraction
    assert ball_scout.attack_timer == 0.5

    ball_tank = MockBall(x=100, y=100)
    ball_tank.ball_type = "tank"
    world_tank = MockWorld()
    world_tank.enemies = [MockEnemy(x=115, y=100)]
    Action(ball_tank, world_tank).execute("attack", 0.0)
    assert ball_tank.attack_timer == 2.0

    ball_default = MockBall(x=100, y=100)
    ball_default.ball_type = "unknown"
    world_default = MockWorld()
    world_default.enemies = [MockEnemy(x=115, y=100)]
    Action(ball_default, world_default).execute("attack", 0.0)
    assert ball_default.attack_timer == 1.0

def test_optimal_skill_usage():
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    world.enemies = [MockEnemy(x=150, y=100)] # Enemy is within 50 range (100 + 10 + 10 + 50 = 170)
    action_layer = Action(ball, world)

    action_layer.execute("attack", 0.0)
    assert ball.used_skill
    assert ball.skill_timer == 5.0 # Reset to cooldown

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
