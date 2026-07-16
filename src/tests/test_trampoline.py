import pytest
from ai.action import Action

class MockWorld(dict):
    def __init__(self):
        super().__init__()
        self.balls = []
        self.arena = None
        self.next_id = 9999

class MockArena(dict):
    def __init__(self):
        super().__init__()
        self.hazards = []
        self.name = 'mock_arena'
        self.weather = 'clear'
    def update_zone(self, tick, delta):
        pass

class MockEntity(dict):
    def __init__(self):
        super().__init__()
        self.id = 1
        self.x = 50.0
        self.y = 50.0
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "basic"
        self.radius = 10.0
        self.speed_boost_timer = 0.0
        self.hazard_immunity_timer = 0.0

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"No attribute {name}")

    def __setattr__(self, name, value):
        self[name] = value

class MockHazard(dict):
    def __init__(self, kind="trampoline", x=50.0, y=50.0, radius=20.0):
        super().__init__()
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True
        self.damage = 0.0

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"No attribute {name}")

    def __setattr__(self, name, value):
        self[name] = value

def test_trampoline_effects():
    world = MockWorld()
    arena = MockArena()
    world.arena = arena
    ball = MockEntity()
    world.balls = [ball]
    action = Action(ball, world)

    hazard = MockHazard(kind="trampoline", x=55.0, y=55.0, radius=20.0)
    arena.hazards = [hazard]

    action.execute("idle", 0.1)

    assert ball.speed_boost_timer >= 1.9
    assert ball.hazard_immunity_timer >= 1.9
    assert ball.vx != 0.0
    assert ball.vy != 0.0
