import pytest
from ai.game_modes import OrbitalCrosshairMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.next_id = 1000
    def add_event(self, type_str, data):
        self.events.append((type_str, data))

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.ball_type = "player"
        self.stamina = 100.0
        self.score = 0

def test_orbital_crosshair_lifecycle():
    mode = OrbitalCrosshairMode()
    world = MockWorld()
    b1 = MockBall(1, 500, 500)
    balls = [b1]

    mode.setup(world, balls)

    # Tick past spawn timer
    mode.tick(world, balls, delta=6.0)

    assert len(mode.crosshairs) == 1
    ch = mode.crosshairs[0]
    assert ch["state"] == "hunting"
    assert ch["target_id"] == 1

    # Manually move target closer to crosshair to simulate locking
    b1.x = ch["x"]
    b1.y = ch["y"]

    # Tick to accumulate timer for locking
    mode.tick(world, balls, delta=2.5)

    assert ch["state"] == "locking"

    # Tick past locking timer to fire
    mode.tick(world, balls, delta=3.5)

    # Crosshair should disappear, hazard should spawn
    assert len(mode.crosshairs) == 0
    assert len(world.arena.hazards) == 1
    h = world.arena.hazards[0]
    assert getattr(h, "kind", "") == "irradiated_zone"

    # Tick to test irradiated zone effect
    initial_stamina = b1.stamina
    initial_hp = b1.hp

    # Ensure ball is inside hazard
    b1.x = h.x
    b1.y = h.y
    mode.tick(world, balls, delta=1.0)

    assert b1.stamina < initial_stamina
    assert b1.hp < initial_hp


def test_orbital_crosshair_tracks_highest_scoring():
    mode = OrbitalCrosshairMode()
    world = MockWorld()

    b1 = MockBall(1, 100, 100)
    b1.score = 50

    b2 = MockBall(2, 900, 900)
    b2.score = 100

    balls = [b1, b2]

    mode.setup(world, balls)

    # Tick past spawn timer
    mode.tick(world, balls, delta=6.0)

    assert len(mode.crosshairs) == 1
    ch = mode.crosshairs[0]
    assert ch["state"] == "hunting"

    # Should initially target b2, which has the highest score
    assert ch["target_id"] == 2

    # Now b1 gets a higher score
    b1.score = 150

    # Tick again
    mode.tick(world, balls, delta=1.0)

    # Should swap target to b1
    assert ch["target_id"] == 1
