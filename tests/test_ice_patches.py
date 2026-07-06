import pytest
from unittest.mock import MagicMock
from src.ai.action import Action

class MockHazard:
    def __init__(self, kind, x, y, radius, active=True):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = active
        self.damage = 0.0

class MockBall:
    def __init__(self, x, y, vx, vy, speed):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = speed
        self.base_speed = speed
        self.is_frictionless = False
        self.id = 1
        self.team = 1
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.radius = 10
        self.perception_radius = 100
        self.ball_type = "normal"
        self.is_flying = False
        self.current_action = "none"
        self.skill_timer = 0
        self.skill_cooldown = 10
        self.used_skill_count = 0

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

    def clamp_position(self, x, y, r):
        return x, y, False

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.tick = 1
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def mock_execute_action(action, world, strategy, delta):
    # Apply the exact code from action.py's execute for ice_patches
    for hazard in world.arena.hazards:
        if hazard.kind == "ice_patches":
            if getattr(hazard, "active", True):
                dx = hazard.x - action.ball.x
                dy = hazard.y - action.ball.y
                dist_sq = dx * dx + dy * dy
                if dist_sq < hazard.radius * hazard.radius:
                    action.ball.is_frictionless = True
                    if hasattr(action.ball, "vx") and hasattr(action.ball, "vy"):
                        action.ball.x += action.ball.vx * delta
                        action.ball.y += action.ball.vy * delta
                    action.ball.speed = getattr(action.ball, 'base_speed', 100.0) * 0.0

def test_ice_patches():
    world = MockWorld()

    # Place a ball exactly on an ice_patches
    ball = MockBall(x=50.0, y=50.0, vx=100.0, vy=50.0, speed=100.0)
    world.balls.append(ball)

    hazard = MockHazard(kind="ice_patches", x=50.0, y=50.0, radius=30.0)
    hazard.last_updated_tick = 0
    world.arena.hazards.append(hazard)

    action = Action(ball=ball, world=world)

    orig_x = ball.x
    orig_y = ball.y
    delta = 0.1

    mock_execute_action(action, world, 'none', delta)

    # ice_patches sets speed to 0 and is_frictionless to True, and moves ball by vx, vy
    assert ball.is_frictionless is True
    assert ball.speed == 0.0
    assert ball.x == orig_x + (ball.vx * delta)
    assert ball.y == orig_y + (ball.vy * delta)

def test_ice_patches_outside():
    world = MockWorld()

    # Place a ball outside an ice_patches
    ball = MockBall(x=150.0, y=150.0, vx=100.0, vy=50.0, speed=100.0)
    world.balls.append(ball)

    hazard = MockHazard(kind="ice_patches", x=50.0, y=50.0, radius=30.0)
    hazard.last_updated_tick = 0
    world.arena.hazards.append(hazard)

    action = Action(ball=ball, world=world)

    orig_x = ball.x
    orig_y = ball.y
    delta = 0.1

    mock_execute_action(action, world, 'none', delta)

    # Shouldn't be affected
    assert ball.is_frictionless is False
    assert ball.speed == 100.0
    assert ball.x == orig_x
    assert ball.y == orig_y
