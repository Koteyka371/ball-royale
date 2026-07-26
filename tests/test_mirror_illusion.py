import pytest
from ai.mirror_illusion import MirrorIllusionMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.entities = []
        self.balls = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y, alive=True, team="blue"):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 10.0
        self.vy = -10.0
        self.radius = 15.0
        self.alive = alive
        self.team = team
        self.ball_type = "default"
        self.mass = 1.0

class MockHazard:
    def __init__(self, x, y, active=True, team=None):
        self.x = x
        self.y = y
        self.radius = 10.0
        self.active = active
        self.team = team

def test_mirror_illusion_setup():
    mode = MirrorIllusionMode()
    world = MockWorld()
    balls = [MockBall(1, 100, 200)]

    mode.setup(world, balls)
    mode.tick(world, balls, 0.1)

    # Illusion should be created
    assert 1 in mode.illusions
    illusion = mode.illusions[1]

    # Should mirror position across 500, 500 (arena center is 500,500, so mirrored is 1000-x, 1000-y)
    assert illusion["x"] == 1000.0 - 100
    assert illusion["y"] == 1000.0 - 200

    # Should invert velocity
    assert illusion["vx"] == -10.0
    assert illusion["vy"] == 10.0

    # Should copy properties
    assert illusion["team"] == "blue"
    assert illusion["radius"] == 15.0
    assert illusion["is_illusion"] is True

    # Should be in world.entities
    assert illusion in world.entities

def test_mirror_illusion_lifecycle():
    mode = MirrorIllusionMode()
    world = MockWorld()
    b = MockBall(1, 100, 200)
    balls = [b]

    mode.setup(world, balls)
    mode.tick(world, balls, 0.1)

    assert len(mode.illusions) == 1
    illusion = mode.illusions[1]
    assert illusion["alive"] is True
    assert illusion in world.entities

    # Ball dies
    b.alive = False
    mode.tick(world, balls, 0.1)

    # Illusion should be removed
    assert len(mode.illusions) == 0
    assert illusion["alive"] is False
    assert illusion not in world.entities

def test_mirror_illusion_absorb_hazard():
    mode = MirrorIllusionMode()
    world = MockWorld()

    b = MockBall(1, 100, 200, team="blue")
    balls = [b]

    # Illusion will spawn at 900, 800 with radius 15
    # Create hazard right on top of the illusion
    h1 = MockHazard(900, 800, team="red")
    world.arena.hazards.append(h1)

    # Create hazard far away
    h2 = MockHazard(100, 100, team="red")
    world.arena.hazards.append(h2)

    # Create hazard on top but same team
    h3 = MockHazard(900, 800, team="blue")
    world.arena.hazards.append(h3)

    mode.setup(world, balls)
    mode.tick(world, balls, 0.1)

    # H1 should be destroyed (absorbed)
    assert h1.active is False
    assert h1 not in world.arena.hazards

    # H2 should remain (far away)
    assert h2.active is True
    assert h2 in world.arena.hazards

    # H3 should remain (same team)
    assert h3.active is True
    assert h3 in world.arena.hazards
