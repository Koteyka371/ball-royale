import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.boosters = []
        self.events = []

class MockArena:
    def __init__(self):
        self.hazards = []
        self.spawn_points = []
        self.radius = 10000

class MockEntity:
    def __init__(self, x, y, kind=None):
        self.x = x
        self.y = y
        self.vx = 5.0
        self.vy = 0.0
        self.kind = kind
        self.radius = 100
        self.hp = 100.0
        self.max_hp = 100.0
        self.id = 1
        self.team = 1
        self.alive = True
        self.speed = 1.0
        self.damage = 10.0
        self.perception_radius = 250.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.badges = []
        self.skill = "idle"
        self.skill_timer = 0
        self.bounces_left = 3
        self.intangible = False
        self.intangible_timer = 0.0
        self.is_intangible = False
        self.target_x = 0
        self.target_y = 0
        self.fire_attachment_timer = 0
        self.ice_attachment_timer = 0
        self.spread_attachment_timer = 0
        self.pierce_attachment_timer = 0
        self.active = True

    def use_skill(self):
        return True

def test_blink_relic_collection():
    world = MockWorld()
    ball = MockEntity(0, 0)
    world.balls.append(ball)
    action = Action(ball, world)

    relic = MockEntity(0, 0, "blink_relic")
    world.boosters.append(relic)

    assert ball.max_hp == 100.0

    ball.x = 0
    ball.y = 0
    relic.x = 0
    relic.y = 0

    action._collect_booster(0.1)

    assert relic not in world.boosters
    assert getattr(ball, "blink_relic_timer", 0) > 14.0
    assert ball.max_hp == 70.0
    assert ball.hp == 70.0
    assert getattr(ball, "blink_relic_tick_timer", 0) > 0.0

def test_blink_relic_tick_and_blink():
    world = MockWorld()
    ball = MockEntity(0, 0)
    ball.max_hp = 70.0
    ball.hp = 70.0
    ball.base_max_hp_blink_relic = 100.0
    ball.blink_relic_timer = 5.0
    ball.blink_relic_applied = True
    ball.blink_relic_tick_timer = 0.1
    ball.vx = 10.0
    ball.vy = 0.0
    world.balls.append(ball)

    action = Action(ball, world)

    action.execute("flee", 0.2)

    assert ball.x > 90.0 # Blinking 100 units forward
    assert getattr(ball, "intangible", False) == True
    assert getattr(ball, "intangible_timer", 0.0) == 0.5
    assert getattr(ball, "blink_relic_tick_timer", 0) >= 2.0

def test_blink_relic_expiration():
    world = MockWorld()
    ball = MockEntity(0, 0)
    ball.max_hp = 70.0
    ball.hp = 70.0
    ball.base_max_hp_blink_relic = 100.0
    ball.blink_relic_timer = 0.1
    ball.blink_relic_applied = True
    world.balls.append(ball)

    action = Action(ball, world)
    action.execute("flee", 0.2)

    assert ball.blink_relic_timer == 0.0
    assert ball.max_hp == 100.0
    assert getattr(ball, "blink_relic_applied", True) == False
