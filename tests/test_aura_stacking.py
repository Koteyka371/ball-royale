import pytest
from ai.action import Action
from arena.procedural_arena import ProceduralArena

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena(800, 600)
        self.balls = []
        self.game_mode = None

class MockBall:
    def __init__(self, bid, btype, x, y):
        self.id = bid
        self.ball_type = btype
        self.team = "blue"
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 50.0
        self.max_hp = 100.0
        self.base_speed = 2.0
        self.speed = 2.0
        self.base_damage = 10.0
        self.damage = 10.0
        self.skill_timer = 0.0

def test_aura_stacking():
    world = MockWorld()
    b1 = MockBall(1, "warrior", 100, 100)
    b2 = MockBall(2, "healer", 110, 100)   # different type, close
    b3 = MockBall(3, "tank", 120, 100)     # different type, close
    b4 = MockBall(4, "archer", 130, 100)   # different type, close
    world.balls = [b1, b2, b3, b4]

    action = Action(b1, world)

    # Base states
    assert b1.hp == 50.0
    assert b1.speed == 2.0
    assert b1.damage == 10.0

    action._apply_friendly_aura(1.0)

    # With 3 other friendly types nearby, should get 3 stacks:
    # 1st stack: +2.0 hp regen (hp should be 52.0)
    # 2nd stack: 1.1x speed (speed should be 2.2)
    # 3rd stack: 1.2x damage (damage should be 12.0)

    assert b1.hp == 52.0
    assert round(b1.speed, 2) == 2.20
    assert round(b1.damage, 2) == 12.00

def test_aura_no_stacking_far():
    world = MockWorld()
    b1 = MockBall(1, "warrior", 100, 100)
    b2 = MockBall(2, "healer", 500, 500)   # too far
    world.balls = [b1, b2]

    action = Action(b1, world)
    action._apply_friendly_aura(1.0)

    # Should get no buffs
    assert b1.hp == 50.0
    assert b1.speed == 2.0
    assert b1.damage == 10.0

def test_aura_same_type_no_stack():
    world = MockWorld()
    b1 = MockBall(1, "warrior", 100, 100)
    b2 = MockBall(2, "warrior", 110, 100)   # same type, close
    world.balls = [b1, b2]

    action = Action(b1, world)
    action._apply_friendly_aura(1.0)

    # Should get no buffs because type is not unique
    assert b1.hp == 50.0
    assert b1.speed == 2.0
    assert b1.damage == 10.0
