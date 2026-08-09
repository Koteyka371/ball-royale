import pytest
from ai.game_modes import SingularityStormMode

class DummyBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.is_spectator = False
        self.is_dashing = False
        self.inventory = []

class DummyArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

def test_singularity_storm_spawns_black_hole():
    mode = SingularityStormMode()
    world = DummyWorld()
    balls = []

    # Tick for 4.9 seconds, shouldn't spawn
    mode.tick(world, balls, delta=4.9)
    assert len(world.arena.hazards) == 0

    # Tick another 0.2 seconds, crosses 5.0 threshold
    mode.tick(world, balls, delta=0.2)
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "mini_black_hole"

def test_singularity_storm_pulls_ball():
    mode = SingularityStormMode()
    world = DummyWorld()
    b = DummyBall(500.0, 500.0)
    balls = [b]

    # Force spawn a black hole at 400, 500
    class DummyHazard:
        def __init__(self):
            self.x = 400.0
            self.y = 500.0
            self.kind = "mini_black_hole"
            self.pull_radius = 300.0
            self.pull_strength = 400.0

    world.arena.hazards.append(DummyHazard())

    mode.tick(world, balls, delta=1.0)

    # Ball should be pulled towards 400, 500. X should decrease.
    assert b.x < 500.0
    assert b.y == 500.0

def test_singularity_storm_dash_mitigates_pull():
    mode = SingularityStormMode()
    world = DummyWorld()
    b = DummyBall(500.0, 500.0)
    b.is_dashing = True
    balls = [b]

    class DummyHazard:
        def __init__(self):
            self.x = 400.0
            self.y = 500.0
            self.kind = "mini_black_hole"
            self.pull_radius = 300.0
            self.pull_strength = 400.0

    world.arena.hazards.append(DummyHazard())

    mode.tick(world, balls, delta=1.0)

    # Ball shouldn't move
    assert b.x == 500.0
    assert b.y == 500.0

def test_singularity_storm_gravity_boots_mitigates_pull():
    mode = SingularityStormMode()
    world = DummyWorld()
    b = DummyBall(500.0, 500.0)
    b.inventory.append("gravity_boots")
    balls = [b]

    class DummyHazard:
        def __init__(self):
            self.x = 400.0
            self.y = 500.0
            self.kind = "mini_black_hole"
            self.pull_radius = 300.0
            self.pull_strength = 400.0

    world.arena.hazards.append(DummyHazard())

    mode.tick(world, balls, delta=1.0)

    # Ball shouldn't move
    assert b.x == 500.0
    assert b.y == 500.0
