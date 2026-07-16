from ai.game_modes import PhantomJuggernautMode
import pytest

class MockBall:
    def __init__(self, id_val, ball_type="normal"):
        self.id = id_val
        self.ball_type = ball_type
        self.alive = True
        self.x = 100.0
        self.y = 100.0
        self.team = "None"
        self.max_hp = 100.0
        self.hp = 100.0
        self.damage = 10.0
        self.radius = 10.0
        self.speed = 100.0
        self.mass = 1.0
        self.is_invisible = False

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.leaderboard_manager = type('MockLB', (), {'data': type('MockData', (), {'get': lambda self, *args: 1})()})()

    def add_event(self, t, data):
        self.events.append((t, data))

def test_phantom_juggernaut_setup():
    mode = PhantomJuggernautMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2), MockBall(3)]

    mode.setup(world, balls)

    # One juggernaut
    juggernauts = [b for b in balls if b.team == "Phantom Juggernaut"]
    assert len(juggernauts) == 1
    jug = juggernauts[0]
    assert jug.is_invisible is True
    assert jug.max_hp == 800.0
    assert jug.damage in [25.0, 50.0]
    assert jug.radius == 20.0

    hunters = [b for b in balls if b.team == "Hunters"]
    assert len(hunters) == 2
    for h in hunters:
        assert h.is_invisible is False
        assert h.max_hp == 80.0

def test_phantom_juggernaut_trail():
    mode = PhantomJuggernautMode()
    world = MockWorld()
    balls = [MockBall(1)]
    mode.setup(world, balls)

    jug = balls[0]

    mode.tick(world, balls, 0.5)

    hazards = world.arena.hazards
    assert len(hazards) == 1
    assert hazards[0].kind == "phantom_trail"

def test_phantom_juggernaut_death():
    mode = PhantomJuggernautMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2)]
    mode.setup(world, balls)

    jug = [b for b in balls if b.team == "Phantom Juggernaut"][0]
    hunter = [b for b in balls if b.team == "Hunters"][0]

    jug.alive = False
    jug.killer = hunter.id

    mode.tick(world, balls, 0.1)

    assert jug.team == "Dead"
    assert jug.is_invisible is False

    assert hunter.team == "Phantom Juggernaut"
    assert hunter.is_invisible is True
