import pytest
from ai.action import Action
import math

class MockBall:
    def __init__(self, id=1, x=0.0, y=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.terminal_velocity = 99999.0
        self.speed_boost_timer = 0.0
        self.max_stamina = 0.0
        self.stamina = 0.0
        self.base_speed = 100.0

class MockHazard:
    def __init__(self, start_x, start_y, end_x, end_y, width, kind="wind_tunnel"):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.radius = width
        self.kind = kind
        self.wind_force = 1500.0
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.hypot(dx, dy)
        self.wind_dir_x = dx / length
        self.wind_dir_y = dy / length
        self.active = True
        self.events = []

class MockArena:
    def __init__(self):
        self.hazards = []
        self.weather = 'clear'
        self.name = 'test_arena'

class MockGameMode:
    def __init__(self):
        self.weather = 'clear'

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.tick_timer = 1.0
        self.time = 1.0
        self.game_mode = MockGameMode()

    def add_event(self, event_type, data=None):
        pass

def test_wind_tunnel_line():
    ball = MockBall(x=500.0, y=500.0)
    world = MockWorld()
    world.balls = [ball]

    hazard = MockHazard(start_x=100.0, start_y=500.0, end_x=900.0, end_y=500.0, width=50.0)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    # The ball is inside the tunnel
    action.execute("", 1.0)
    assert ball.vx > 1000.0

    # Outside tunnel
    ball.x = 500.0
    ball.y = 600.0
    ball.vx = 0.0
    action.execute("", 1.0)
    assert ball.vx < 100.0
