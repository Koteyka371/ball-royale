import pytest
from ai.action import Action
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, x=0.0, y=0.0, stamina=100.0, max_stamina=100.0):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.hp = 100.0
        self.speed = 2.0
        self.team = "A"
        self.stamina = stamina
        self.max_stamina = max_stamina
        self.stun_timer = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.is_foggy = False
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 5000

    def update_zone(self, tick, delta):
        pass

    def clamp_position(self, x, y, radius):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.tick = 0
        self.events = []

    def add_event(self, *args, **kwargs):
        pass

    def _deal_damage(self, attacker, target, damage=None):
        pass

def test_jump_pad_high_stamina():
    ball = MockBall(100.0, 100.0, stamina=100.0)
    world = MockWorld()
    world.balls.append(ball)

    pad = Hazard(1, 100.0, 100.0, 30.0, "jump_pad", 0.0)
    pad.target_x = 500.0
    pad.target_y = 500.0
    world.arena.hazards.append(pad)

    action = Action(ball, world)
    action.execute("idle", 0.016)

    assert getattr(ball, "is_flying", False) == True
    assert getattr(ball, "fly_timer", 0.0) > 0.0
    assert getattr(ball, "fly_target_x", None) == 500.0
    assert getattr(ball, "fly_target_y", None) == 500.0
    assert abs(ball.stamina - 50.0) < 1.0 # 100.0 - 50.0
    assert getattr(ball, "stun_timer", 0.0) == 0.0

def test_jump_pad_low_stamina():
    ball = MockBall(100.0, 100.0, stamina=10.0)
    world = MockWorld()
    world.balls.append(ball)

    pad = Hazard(1, 100.0, 100.0, 30.0, "jump_pad", 0.0)
    pad.target_x = 500.0
    pad.target_y = 500.0
    world.arena.hazards.append(pad)

    action = Action(ball, world)
    action.execute("idle", 0.016)

    assert getattr(ball, "is_flying", False) == False
    assert getattr(ball, "fly_timer", 0.0) == 0.0
    assert getattr(ball, "stun_timer", 0.0) >= 1.9
