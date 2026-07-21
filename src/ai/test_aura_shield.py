import pytest

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.level = 10
        self.cosmetic_aura_color = (1.0, 0.0, 0.0, 1.0)
        self.team = "red"
        self.shield = 0.0
        self.alive = True

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.events = []

    def get_nearby_entities(self, ball, radius):
        return {"allies": [b for b in self.balls if b != ball], "enemies": []}

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_aura_shield_logic():
    from ai.action import Action

    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 5, 5) # Colliding

    world = MockWorld([b1, b2])
    action = Action(b1, world)

    action._resolve_collisions()

    assert b1.shield == 30.0
    assert b2.shield == 30.0

    shield_events = [e for e in world.events if e[0] == "aura_shield"]
    assert len(shield_events) == 2

    # Check cooldown
    action._resolve_collisions()
    assert b1.shield == 30.0
    assert b2.shield == 30.0

def test_aura_shield_mismatch_color():
    from ai.action import Action

    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 5, 5)
    b2.cosmetic_aura_color = (0.0, 1.0, 0.0, 1.0)

    world = MockWorld([b1, b2])
    action = Action(b1, world)

    action._resolve_collisions()

    assert b1.shield == 0.0
    assert b2.shield == 0.0

def test_aura_shield_mismatch_team():
    from ai.action import Action

    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 5, 5)
    b2.team = "blue"

    world = MockWorld([b1, b2])
    action = Action(b1, world)

    action._resolve_collisions()

    assert b1.shield == 0.0
    assert b2.shield == 0.0
