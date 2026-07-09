import pytest
from unittest.mock import MagicMock
from ai.action import Action

class MockWorld:
    def __init__(self, tick):
        self.tick = tick
        self.arena = MagicMock()
        self.arena.hazards = []
        self.arena.safe_zone_center = (500, 500)
        self.arena.safe_zone_radius = 5000
        self.arena.clamp_position = lambda x,y,r: (x, y, False)
        self.entities = []
        self.gravity = 9.8

class MockBall:
    def __init__(self, stamina=100.0, skill_timer=0.0):
        self.stamina = stamina
        self.skill_timer = skill_timer
        self.max_stamina = 100.0
        self.team = "NO_TEAM"
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.radius = 10
        self.alive = True
        self.active_effects = {}
        self.team = "blue"
        self.ball_type = "warrior"
        self.has_meta = lambda x: False
        self.speed = 100

    def get_meta(self, k): return None

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.x = 0
        self.y = 0
        self.radius = 50
        self.damage = 0
        self.active = True
        self.team = "NO_TEAM"

def test_stamina_drain_zone_no_pulse():
    world = MockWorld(119) # Not 120
    world.arena.hazards = [MockHazard("stamina_drain_zone")]

    ball = MockBall(stamina=0.0, skill_timer=0.0)
    action = Action(ball, world)
    action._idle = lambda d: None
    action.execute("dummy", 0.016)

    assert ball.skill_timer == 0.0

def test_stamina_drain_zone_pulse_with_stamina():
    world = MockWorld(120) # Pulse tick!
    world.arena.hazards = [MockHazard("stamina_drain_zone")]

    ball = MockBall(stamina=10.0, skill_timer=0.0)
    action = Action(ball, world)
    action._idle = lambda d: None
    action.execute("dummy", 0.016)

    assert ball.skill_timer == 0.0
    assert ball.stamina < 10.0

def test_stamina_drain_zone_pulse_zero_stamina():
    world = MockWorld(120) # Pulse tick!
    world.arena.hazards = [MockHazard("stamina_drain_zone")]

    ball = MockBall(stamina=0.0, skill_timer=0.0)
    action = Action(ball, world)
    action._idle = lambda d: None
    action.execute("dummy", 0.016)

    # It might be decremented by delta (0.016 or similar) during the same tick's update
    assert 0.9 <= ball.skill_timer <= 1.0
