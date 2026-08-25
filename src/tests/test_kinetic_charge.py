import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, r):
        # Always simulate a bounce
        return x, y, True

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000

    def add_event(self, t, d):
        self.events.append({'type': t, 'data': d})

    def get_nearby_entities(self, ball, radius):
        return [b for b in getattr(self, "balls", []) if b is not ball]

class MockBall:
    def __init__(self, trait="kinetic_charge"):
        self.id = 1
        self.x = 10.0
        self.y = 10.0
        self.vx = 10.0
        self.vy = 10.0
        self.trait = trait
        self.team = "A"

class MockEnemy:
    def __init__(self):
        self.id = 2
        self.x = 20.0 # close enough to trigger collision
        self.y = 20.0
        self.vx = 0.0
        self.vy = 0.0
        self.team = "B"

def test_kinetic_charge():
    w = MockWorld()
    b = MockBall("kinetic_charge")
    a = Action(b, w)

    # Initially 0
    assert getattr(b, "kinetic_charge", 0) == 0
    assert getattr(b, "kinetic_charge_ready", False) == False

    # Simulate 3 bounces
    for _ in range(3):
        a._clamp_position()

    assert getattr(b, "kinetic_charge", 0) == 3
    assert getattr(b, "kinetic_charge_ready", False) == True

    # Collision with enemy
    e = MockEnemy()
    w.balls = [b, e]
    w.get_nearby_entities = lambda *args: [e]

    a._resolve_collisions()

    # Ready flag should be consumed
    assert getattr(b, "kinetic_charge_ready", False) == False
    assert getattr(b, "kinetic_charge", 0) == 0

    # Events should contain kinetic_shockwave
    assert any(e['type'] == 'visual_effect' and e['data'].get('type') == 'kinetic_shockwave' for e in w.events)
