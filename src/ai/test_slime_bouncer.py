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
        self.slow_timer = kwargs.get('slow_timer', 0.0)

    # Allows dict-like access
    def get(self, key, default=None):
        return getattr(self, key, default)

class MockArena:
    def __init__(self):
        self.hazards = []
    def update_zone(self, tick, delta): pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.hazards = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": [], "hazards": self.hazards}

def test_slime_bouncer():
    # Ball is moving right and down towards the hazard
    ball = MockEntity(x=50.0, y=50.0, vx=100.0, vy=100.0)
    world = MockWorld()
    class SlimeBouncer:
        def __init__(self):
            self.id = 1
            self.x = 60.0
            self.y = 60.0
            self.radius = 20.0
            self.kind = 'slime_bouncer'
            self.damage = 0.0
    world.arena.hazards.append(SlimeBouncer())
    action = Action(ball, world)
    action.execute('idle', 0.1)

    # Velocity should be reversed and scaled up to 1500
    # vx was 100, vy was 100
    # expected vector is -x, -y -> vx should be negative, vy should be negative
    assert ball.vx < 0.0
    assert ball.vy < 0.0
    # Action execution will apply speed limits, so we check if it bounced effectively
    assert ball.vx < -100.0
    assert ball.vy < -100.0
    assert ball.slow_timer >= 2.9
