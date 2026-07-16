import math
from ai.action import Action

class MockEntity:
    def __init__(self, **kwargs):
        self.x = kwargs.get('x', 0.0)
        self.y = kwargs.get('y', 0.0)
        self.vx = kwargs.get('vx', 0.0)
        self.vy = kwargs.get('vy', 0.0)
        self.radius = kwargs.get('radius', 10.0)
        self.ball_type = kwargs.get('ball_type', 'basic')
        self.speed_boost_timer = kwargs.get('speed_boost_timer', 0.0)
        self.hazard_immunity_timer = kwargs.get('hazard_immunity_timer', 0.0)
        self.suspended_projectiles = []
        self.state_history = []
        self._chrono_slow = False

    # Allows dict-like access
    def get(self, key, default=None):
        return getattr(self, key, default)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

class MockArena:
    def __init__(self):
        self.name = 'mock_arena'
        self.weather = 'clear'
        self.hazards = []
    def update_zone(self, tick, delta): pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.next_id = 9999
        self.hazards = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": [], "hazards": self.hazards}

def test_trampoline():
    ball = MockEntity(x=50.0, y=50.0)
    world = MockWorld()
    class Trampoline:
        def __init__(self):
            self.id = 1
            self.x = 55.0
            self.y = 55.0
            self.radius = 20.0
            self.kind = 'trampoline'
            self.damage = 0.0
    world.arena.hazards.append(Trampoline()) # Add to arena hazards for Python implementation
    action = Action(ball, world)
    action.execute('idle', 0.1)

    assert ball.vx != 0.0
    assert ball.vy != 0.0
    assert ball.speed_boost_timer >= 1.9
    assert ball.hazard_immunity_timer >= 1.9
