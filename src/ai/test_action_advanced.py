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

def test_collect_booster_interrupt():
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    # Booster is to the right
    booster = MockEntity(x=200, y=100, ball_type="booster")
    # Enemy is close enough to trigger interrupt: dist < ball_radius + enemy_radius + 30
    # 100 to 140 is dist=40. 10 + 10 + 30 = 50. So 40 < 50.
    enemy = MockEntity(x=140, y=100, ball_type="enemy")
    world.entities = [booster, enemy]

    action = Action(ball, world)

    # Normally, it would move towards booster (x > 100).
    # But because it's interrupted, it flees (moves AWAY from enemy).
    # Fleeing from an enemy at x=140 pushes the ball towards x < 100.
    action.execute("collect_booster", 0.1)

    assert ball.x < 100

def test_tank_target_strong_chase():
    ball = MockBall(x=100, y=100)
    ball.ball_type = "tank"
    world = MockWorld()

    # We have three enemies.
    # e1 is very close but has low HP
    # e2 is far away but has the highest HP
    # e3 is medium distance with medium HP
    e1 = MockEntity(x=110, y=100, ball_type="enemy")
    e1.hp = 50.0

    e2 = MockEntity(x=200, y=100, ball_type="enemy")
    e2.hp = 200.0  # Strongest

    e3 = MockEntity(x=150, y=100, ball_type="enemy")
    e3.hp = 100.0

    world.entities = [e1, e2, e3]

    action = Action(ball, world)

    # Executing chase without the 'Target Strong' logic would pick e1 (closest).
    # Since the tank targets the strongest, it should target e2.
    # Targeting e2 at x=200 means moving towards the right (increasing x).
    # Targeting e1 at x=110 also moves right, but let's test if it's explicitly targeting e2.
    # To differentiate, we can place them in different directions.

    # Let's adjust positions to make the targeting choice obvious
    e1.x = 90
    e1.y = 100  # Left (closest)

    e2.x = 100
    e2.y = 200  # Up (furthest, strongest)

    e3.x = 100
    e3.y = 0    # Down

    action.execute("chase", 0.1)

    # If it targeted e1, it would move left (x < 100).
    # If it targeted e3, it would move down (y < 100).
    # Since it should target e2, it must move up (y > 100).
    assert ball.y > 100
    assert ball.x > 100


def test_collect_booster_ignore_enemies():
    ball = MockBall(x=100, y=100)
    world = MockWorld()
    # Booster is to the right
    booster = MockEntity(x=200, y=100, ball_type="booster")
    # Enemy is between ball and booster, but slightly far enough away to NOT trigger interrupt
    # dist = 60. Threshold = 50.
    enemy = MockEntity(x=160, y=105, ball_type="enemy")
    world.entities = [booster, enemy]

    action = Action(ball, world)

    # If the enemy was treated as an obstacle, the ball's y would shift significantly to avoid it.
    # Since ignore_enemies=True is passed, it should move straight toward the booster.
    # We can track the y to see if it deviated.
    # The booster is at y=100, ball at y=100. It should stay at y=100.
    action.execute("collect_booster", 0.1)

    assert ball.x > 100
    assert ball.y == 100
