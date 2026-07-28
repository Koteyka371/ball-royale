import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []
        self.boundary_states = {"top": "wall", "bottom": "wall", "left": "wall", "right": "wall"}

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type_str, payload):
        self.events.append((type_str, payload))

class MockBall:
    def __init__(self, bid, x, y):
        self.id = bid
        self.x = x
        self.y = y
        self.radius = 10.0
        self.alive = True
        self.base_speed_multiplier = 1.0
        self.speed_multiplier = 1.0
        self.bumper_frenzy_multiplier = 0.0

def test_bumper_frenzy_spawns_bumpers():
    mode = GAME_MODES["bumper_frenzy"]
    world = MockWorld()
    balls = [MockBall(1, 100, 100)]

    mode.setup(world, balls)

    assert len(world.arena.hazards) == 20
    assert world.arena.hazards[0]["kind"] == "bumper_frenzy_bumper"

def test_bumper_frenzy_multiplier():
    mode = GAME_MODES["bumper_frenzy"]
    world = MockWorld()

    # Place a ball directly on a bumper
    ball = MockBall(1, 500, 500)
    balls = [ball]

    mode.setup(world, balls)

    # Force a bumper onto the ball
    world.arena.hazards[0]["x"] = 500
    world.arena.hazards[0]["y"] = 500

    mode.tick(world, balls, delta=0.016)

    # Should gain multiplier
    assert ball.bumper_frenzy_multiplier > 0.0
    assert ball.speed_multiplier > 1.0

def test_bumper_frenzy_shatter():
    mode = GAME_MODES["bumper_frenzy"]
    world = MockWorld()

    # Place ball at boundary with max speed
    ball = MockBall(1, 0, 500) # Left wall
    ball.bumper_frenzy_multiplier = 2.0
    ball.base_speed_multiplier = 1.0

    balls = [ball]

    mode.setup(world, balls)
    world.arena.boundary_states = {"top": "wall", "bottom": "wall", "left": "wall", "right": "wall"}

    mode.tick(world, balls, delta=0.016)

    # Left wall should shatter
    assert world.arena.boundary_states["left"] == "abyss"
    assert any(e[0] == "visual_effect" and e[1]["type"] == "glass_shatter" for e in world.events)
