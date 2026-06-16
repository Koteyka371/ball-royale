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

class MockAlly:
    def __init__(self, x=10, y=0, radius=10, ball_type="mock_ball", alive=True):
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
    # y is no longer exactly 100 because the "pull towards center" logic alters the movement vector.
    # The center is 500,500, so y should increase slightly.
    assert ball.y >= 100

def test_execute_chase():
    # Test simple chase
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    world.enemies = [MockEnemy(x=200, y=100)] # Enemy to the right
    action_layer = Action(ball, world)

    action_layer.execute("chase", 0.1)
    assert ball.current_action == "chase"
    assert ball.x > 100 # Moved right towards enemy
    assert ball.y == 100
    assert not world.dealt_damage # Should not deal damage, too far

    # Test stopping at attack range
    ball2 = MockBall(x=100, y=100)
    world2 = MockWorld()
    world2.enemies = [MockEnemy(x=115, y=100)] # Enemy is close (10+10+5 = 25 attack range. distance is 15 <= 25)
    action_layer2 = Action(ball2, world2)
    action_layer2.execute("chase", 0.1)
    assert world2.dealt_damage # Should deal damage

    # Test obstacle avoidance
    ball3 = MockBall(x=100, y=100)
    world3 = MockWorld()
    # Target is right. Obstacle is right but slightly closer
    target = MockEnemy(x=200, y=100)
    obstacle = MockEnemy(x=125, y=100)
    world3.enemies = [target, obstacle]
    action_layer3 = Action(ball3, world3)
    action_layer3.execute("chase", 0.1)
    # Should move right, but the obstacle is exactly in the way, meaning repel will push away from it.
    # We should have repel_x < 0 pushing ball left, neutralizing or overcoming target push
    # To test more reliably, put obstacle slightly off-axis

    ball4 = MockBall(x=100, y=100)
    world4 = MockWorld()
    # The obstacle must be further than the target, otherwise it becomes the target!
    # Target is close-ish, say 150, 100.
    target4 = MockEnemy(x=150, y=100)
    # Obstacle is further away but on the way: 120, 110. Wait, 120 is closer than 150!
    # If obstacle is closer, it becomes the target. We want to test repulsion from an entity that IS NOT the target.
    # What if the obstacle is an ally? Yes!
    obstacle4 = MockAlly(x=110, y=110) # Ally down-right
    world4.enemies = [target4]
    world4.allies = [obstacle4]

    # Need to modify MockWorld to return allies
    def mock_get_nearby(ball, radius):
        return {
            "enemies": world4.enemies,
            "allies": world4.allies,
            "boosters": [],
            "traps": []
        }
    world4.get_nearby_entities = mock_get_nearby

    action_layer4 = Action(ball4, world4)
    action_layer4.execute("chase", 0.1)

    # Repel from ally at (110,110) pushes ball up-left (negative Y)
    # Target at (150,100) pulls ball right (neutral Y)
    # So ball y should be < 100
    assert ball4.y < 100

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

    action_layer.execute("use skill", 0.1)
    assert ball.current_action == "use skill"
    assert ball.used_skill

def test_execute_idle_fallback():
    ball = MockBall()
    world = MockWorld()
    action_layer = Action(ball, world)

    action_layer.execute("unknown_strategy", 0.1)
    assert ball.current_action == "unknown_strategy"

def test_execute_attack_timing():
    ball = MockBall(x=100, y=100)
    ball.ball_type = "tank" # Slow attack (1.5s)
    world = MockWorld()
    world.enemies = [MockEnemy(x=115, y=100)] # Close enemy
    action_layer = Action(ball, world)

    # First attack, should deal damage and set cooldown
    action_layer.execute("attack", 0.1)
    assert world.dealt_damage
    assert ball.attack_timer > 1.0 # Should be 1.5

    # Reset damage flag
    world.dealt_damage = False

    # Second attack immediately, should be on cooldown
    action_layer.execute("attack", 0.1)
    assert not world.dealt_damage
    assert ball.attack_timer < 1.5 # Should have decreased by delta

def test_execute_attack_skill():
    ball = MockBall(x=100, y=100)
    ball.ball_type = "bomber"
    world = MockWorld()
    world.enemies = [
        MockEnemy(x=110, y=100),
        MockEnemy(x=105, y=105)
    ]
    action_layer = Action(ball, world)

    action_layer.execute("attack", 0.1)

    assert ball.used_skill
    assert ball.skill_timer > 0.0
