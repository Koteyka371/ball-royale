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
        self.facing_x = 0.0
        self.facing_y = 1.0

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
        self.last_damage_dealt = getattr(ball, "damage", 0)

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

def test_flanking_ninja():
    ball = MockBall(x=100, y=100)
    ball.personality = "ninja"
    ball.damage = 10

    world = MockWorld()
    enemy = MockEnemy(x=100, y=150)
    # Enemy is facing down (0, 1)
    enemy.facing_x = 0.0
    enemy.facing_y = 1.0
    world.enemies = [enemy]

    action_layer = Action(ball, world)

    # Ball is above enemy (y=100 vs y=150). Enemy faces down.
    # The dot product of vector from ball to enemy (0, 1) and enemy facing (0, 1) is 1.0 > 0.5.
    # Therefore, ball is considered behind the enemy! It should just move straight and deal double damage.

    # Move ball closer so it can hit
    ball.y = 135
    action_layer.execute("attack", 0.1)
    assert world.dealt_damage
    assert world.last_damage_dealt == 20  # Double damage from behind

    # Now test flanking movement when NOT behind target
    ball2 = MockBall(x=100, y=200)
    ball2.personality = "ninja"
    # Enemy faces down, ball is below enemy (y=200 vs y=150). Vector from ball to enemy is (0, -1).
    # Dot product is -1.0. Ball is IN FRONT of enemy.
    world2 = MockWorld()
    world2.enemies = [enemy]

    action_layer2 = Action(ball2, world2)
    # Ensure ball starts with no facing so it gets created
    action_layer2.execute("attack", 0.1)

    # It should steer towards behind the enemy (which is y < 150)
    # The point behind the enemy is roughly x=100, y=150 - (10+10+20) = 110.
    # Ball should move UP towards y=110, so its y should decrease.
    assert ball2.y < 200
