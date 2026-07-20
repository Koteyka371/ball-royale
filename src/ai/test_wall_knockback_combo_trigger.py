import pytest
import sys
sys.path.append('src')
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 20.0
        self.alive = True
        self.hp = 100.0
        self.vx = 600.0
        self.vy = 0.0
        self.damage = 10.0

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, r):
        return x, y, True

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.width = 1000
        self.height = 1000
        self.events = []
        self.game_mode = None
        self.arena = MockArena()

    def add_event(self, type, data):
        self.events.append({'type': type, 'data': data})

    def get_nearby_entities(self, pos, radius):
        return {"enemies": [], "allies": []}

def test_wall_knockback_combo_trigger():
    b1 = MockBall(1, 100, 100)
    world = MockWorld([b1])

    action = Action(b1, world)
    action.execute("idle", 0.1) # Executes tick which calls clamp_position and bounce logic

    assert getattr(b1, "_wall_knockback_combo_timer", 0.0) > 1.3

if __name__ == "__main__":
    pytest.main([__file__])
