import pytest
from ai.game_modes import GameMode

class MockHazard:
    def __init__(self, kind, x, y, radius=50.0):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius

class MockBall:
    def __init__(self, id, x, y, vx, vy, radius=15.0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.alive = True
        self.ball_type = "normal"

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

def test_momentum_mirror():
    world = MockWorld()
    hazard = MockHazard("momentum_mirror", 100.0, 100.0, 50.0)
    world.arena.hazards.append(hazard)

    # Ball inside
    ball1 = MockBall(1, 100.0, 100.0, 10.0, 5.0)
    # Ball outside
    ball2 = MockBall(2, 300.0, 300.0, -10.0, -5.0)

    balls = [ball1, ball2]

    mode = GameMode()
    mode.apply_dynamic_traits(world, balls, 0.016)

    # Ball 1 should have its velocity flipped
    assert ball1.vx == -10.0
    assert ball1.vy == -5.0

    # Ball 2 should be unaffected
    assert ball2.vx == -10.0
    assert ball2.vy == -5.0

    # Check that an event was generated
    assert len(world.events) == 1
    assert world.events[0]["type"] == "mirror_bounce"

    # Run again, ball 1 shouldn't flip again because it's still inside
    mode.apply_dynamic_traits(world, balls, 0.016)
    assert ball1.vx == -10.0
    assert ball1.vy == -5.0

    # Move ball 1 outside
    ball1.x = 200.0
    mode.apply_dynamic_traits(world, balls, 0.016)

    # Move it back inside
    ball1.x = 100.0
    mode.apply_dynamic_traits(world, balls, 0.016)

    # It should flip again
    assert ball1.vx == 10.0
    assert ball1.vy == 5.0
