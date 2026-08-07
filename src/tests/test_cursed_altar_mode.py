import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.radius = 10.0
        self.hp = 100.0
        self.speed = 100.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.balls = []

    def add_event(self, type, data):
        self.events.append((type, data))


def test_cursed_altar_mode_setup():
    mode = GAME_MODES["cursed_altar"]
    world = MockWorld()
    mode.setup(world)

    assert hasattr(mode, "altars")
    assert len(mode.altars) == 1
    assert mode.altars[0]["x"] == 500.0
    assert mode.altars[0]["y"] == 500.0
    assert mode.altars[0]["radius"] == 150.0
    assert mode.altars[0]["capture_progress"] == 0.0
    assert mode.altars[0]["owner"] is None
    assert mode.altars[0]["curse_timer"] == 3.0


def test_cursed_altar_capture_and_curse():
    mode = GAME_MODES["cursed_altar"]
    world = MockWorld()
    mode.setup(world)

    # Ball inside altar
    b1 = MockBall(1, 500, 500, "team_a")
    world.balls = [b1]

    # Tick to start capture
    mode.tick(world, [b1], delta=1.0)
    assert mode.altars[0]["owner"] == "team_a"
    assert mode.altars[0]["capture_progress"] > 0.0

    # Fast forward just before curse
    mode.tick(world, [b1], delta=1.9)
    assert b1.hp == 100.0
    assert b1.speed == 100.0

    # Trigger curse
    mode.tick(world, [b1], delta=0.2)
    assert mode.altars[0]["curse_timer"] == 3.0
    assert b1.hp == 95.0
    assert b1.speed == 80.0

    # Another curse after 3 seconds
    mode.tick(world, [b1], delta=3.0)
    assert b1.hp == 90.0
    assert b1.speed == 64.0

def test_cursed_altar_decay():
    mode = GAME_MODES["cursed_altar"]
    world = MockWorld()
    mode.setup(world)

    # Ball inside altar
    b1 = MockBall(1, 500, 500, "team_a")
    world.balls = [b1]

    # Tick to start capture
    mode.tick(world, [b1], delta=1.0)
    assert mode.altars[0]["owner"] == "team_a"
    assert mode.altars[0]["capture_progress"] > 0.0

    # Ball leaves altar
    b1.x = 0
    b1.y = 0

    mode.tick(world, [b1], delta=1.0)
    assert mode.altars[0]["capture_progress"] < 20.0

def test_cursed_altar_contested():
    mode = GAME_MODES["cursed_altar"]
    world = MockWorld()
    mode.setup(world)

    # Ball inside altar
    b1 = MockBall(1, 500, 500, "team_a")
    world.balls = [b1]

    # Tick to capture
    mode.tick(world, [b1], delta=1.0)
    assert mode.altars[0]["owner"] == "team_a"
    assert mode.altars[0]["capture_progress"] > 0.0

    # Another team enters
    b2 = MockBall(2, 500, 500, "team_b")
    world.balls = [b1, b2]

    # Progress should decay
    old_prog = mode.altars[0]["capture_progress"]
    mode.tick(world, [b1, b2], delta=0.5)

    assert mode.altars[0]["capture_progress"] < old_prog
