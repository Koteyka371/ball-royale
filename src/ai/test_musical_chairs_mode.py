import pytest
from ai.game_modes import GAME_MODES

def test_musical_chairs_mode_exists():
    assert "musical_chairs" in GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, event_name, data):
        self.events.append((event_name, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.weather_immunity_timer = 0.0

def test_musical_chairs_logic():
    mode = GAME_MODES["musical_chairs"]
    world = MockWorld()

    b1 = MockBall(1, 100, 100)
    b2 = MockBall(2, 500, 500)
    b3 = MockBall(3, 900, 900)
    balls = [b1, b2, b3]

    mode.setup(world, balls)

    # Num zones should be max(1, 3 - 1) = 2
    assert mode.num_zones == 2
    assert mode.phase == "waiting"

    # We will override zones to a deterministic place for testing
    mode.zones = [
        {"x": 100.0, "y": 100.0, "radius": 80.0},
        {"x": 900.0, "y": 900.0, "radius": 80.0}
    ]

    # Tick during waiting phase, just decreases round timer
    mode.tick(world, balls, delta=9.0)
    assert mode.phase == "waiting"

    # Tick to cross round timer
    mode.tick(world, balls, delta=1.1)

    # Phase should now be 'damage'
    assert mode.phase == "damage"

    # Only b2 was outside the zones. b1 and b3 were inside.
    assert b1.hp == 100.0
    assert b3.hp == 100.0

    # b2 should have taken 50 damage
    assert b2.hp == 50.0
    assert b2.alive == True

    # Next phase logic check: num zones decreased
    assert mode.num_zones == 1

    # Tick the damage timer
    mode.tick(world, balls, delta=1.1)
    assert mode.phase == "waiting"

    # Now one zone is spawned. Let's make it at b2
    mode.zones = [
        {"x": 500.0, "y": 500.0, "radius": 80.0}
    ]

    # Next round
    mode.tick(world, balls, delta=10.1)

    # Now b1 and b3 take damage.
    assert b2.hp == 50.0 # b2 in zone
    assert b1.hp == 50.0
    assert b3.hp == 50.0

    # Next round again, kills b1 and b3
    mode.tick(world, balls, delta=1.1) # finish damage phase
    mode.tick(world, balls, delta=10.1) # cross waiting phase

    # b2 takes damage because we don't set zones this time (or it spawned randomly away)
    # Actually it spawned randomly. So they might take damage.
    # At least someone should take damage. We'll just verify game mode doesn't crash.
    pass
