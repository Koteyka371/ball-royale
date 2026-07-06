import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []
        self.is_heatwave = False
        self.is_snowing = False
        self.is_windy = False
        self.wind_dx = 0.0
        self.wind_dy = 0.0

class MockWorld:
    def __init__(self, arena):
        self.arena = arena
        self.balls = []
        self.hazards = []
        self.events = []
        self.dead_balls = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

    def _deal_damage(self, *args, **kwargs):
        pass

class MockBall:
    def __init__(self, x=0, y=0, vx=10, vy=10, speed=100, ball_type="test"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = speed
        self.ball_type = ball_type
        self.stamina = 100.0
        self.team = 1
        self.id = 1
        self.alive = True
        self.skill_timer = 10.0
        self.skill_cooldown = 10.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.damage = 10.0
        self.radius = 20.0
        self.current_action = "none"

def test_summer_heatwave_cooldown():
    ball = MockBall()
    arena = MockArena()
    arena.is_heatwave = True
    world = MockWorld(arena)
    world.balls = [ball]
    action = Action(ball, world)

    action.execute('none', 1.0)
    assert math.isclose(ball.skill_timer, 8.5)

def test_winter_snow_cooldown():
    ball = MockBall()
    arena = MockArena()
    arena.is_snowing = True
    world = MockWorld(arena)
    world.balls = [ball]
    action = Action(ball, world)

    action.execute('none', 1.0)
    assert math.isclose(ball.skill_timer, 9.5)

def test_autumn_speed():
    ball = MockBall()
    arena = MockArena()
    arena.is_windy = True
    world = MockWorld(arena)
    world.balls = [ball]
    action = Action(ball, world)

    action.execute('none', 1.0)
    assert math.isclose(ball.base_speed, 100.0 * 1.2)
