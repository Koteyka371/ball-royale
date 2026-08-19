import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000
        self.balls = []
        self.items = []
        self.events = []

class MockBall:
    def __init__(self, x, y, team=1, id="mock_ball"):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.team = team
        self.id = id
        self.traits = []
        self.alive = True
        self.hp = 100
        self.speed_debuff_timer = 0
        self.speed_debuff_multiplier = 1.0
        self.intangible = False
        self.skill = "grapple"
        self.active_skill = "grapple"
        self.skill_timer = 0
        self.inventory = []
        self.SKILL_COOLDOWN = 5.0

    def has_meta(self, meta):
        return hasattr(self, meta)

    def __repr__(self):
        return f"MockBall({self.x}, {self.y})"

def test_heavy_grapple_pull():
    # Test ball without trait pulling an enemy
    world = MockWorld()
    ball1 = MockBall(500, 500, team=1)
    target_enemy1 = MockBall(550, 500, team=2) # 50 away, wall is 500 away. So it grabs target.
    world.balls = [ball1, target_enemy1]

    action1 = Action(ball1, world)
    action1._use_skill()

    # 550 - (dx/dist)*pull_dist*0.2 -> dx=50, dist=50, so - (1) * 200 * 0.2 = -40
    # Expected target_enemy1.x = 510
    assert math.isclose(target_enemy1.x, 510.0)

    # Test ball with trait pulling an enemy
    world2 = MockWorld()
    ball2 = MockBall(500, 500, team=1)
    ball2.traits = ["heavy_grapple"]
    target_enemy2 = MockBall(550, 500, team=2)
    world2.balls = [ball2, target_enemy2]

    action2 = Action(ball2, world2)
    action2._use_skill()

    # Pull dist base becomes 300, 300*0.2 = 60
    # target_enemy2.x = 550 - 60 = 490.0
    assert math.isclose(target_enemy2.x, 490.0)

def test_heavy_grapple_hook_self():
    world = MockWorld()

    class MockHazard:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.kind = "hazard"
            self.radius = 15.0

    hazard1 = MockHazard(550, 500)
    world.arena.hazards = [hazard1]

    ball3 = MockBall(500, 500, team=1)
    ball3.skill = "grapple_hook"
    ball3.active_skill = "grapple_hook"
    world.balls = [ball3]
    action3 = Action(ball3, world)
    action3._use_skill()

    v_no_trait = ball3.vx

    hazard2 = MockHazard(550, 500)
    world.arena.hazards = [hazard2]
    ball4 = MockBall(500, 500, team=1)
    ball4.skill = "grapple_hook"
    ball4.active_skill = "grapple_hook"
    ball4.traits = ["heavy_grapple"]
    world.balls = [ball4]
    action4 = Action(ball4, world)
    action4._use_skill()

    v_with_trait = ball4.vx

    assert v_with_trait > v_no_trait
