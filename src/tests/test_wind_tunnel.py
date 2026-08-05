import pytest
from ai.action import Action

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
    def __init__(self, x=0.0, y=0.0, radius=150.0, kind="wind_tunnel"):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.wind_force = 1500.0
        self.wind_dir_x = 1.0
        self.wind_dir_y = 0.0
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

def test_wind_tunnel_hazard_pushes_ball():
    ball = MockBall(x=100.0, y=100.0)
    world = MockWorld()
    world.balls = [ball]

    hazard = MockHazard(x=100.0, y=100.0, radius=100.0)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    # Give the ball a large terminal velocity so it doesn't get capped by physics simulation
    ball.terminal_velocity = 99999.0
    action.execute("", 1.0)

    # Check that vx is increased significantly
    assert ball.vx > 1000.0
    assert abs(ball.vy) < 5.0

    # Move out of range
    ball.x = 500.0
    old_vx = ball.vx
    action.execute("", 1.0)
    # Shouldn't increase further
    assert ball.vx < 100.0
