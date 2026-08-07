import pytest
from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x=500.0, y=500.0, hp=100.0, alive=True):
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = alive
        self.id = 1
        self.weather_immunity_timer = 0.0

class MockArena:
    def __init__(self, width=1000.0, height=1000.0):
        self.width = width
        self.height = height

class MockWorld:
    def __init__(self, width=1000.0, height=1000.0):
        self.arena = MockArena(width, height)
        self.dead_balls = []
        self.events = []
        self.weekly_mutator = ""
        self.mutators_active = False

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_converging_safe_zones_setup():
    mode = GAME_MODES["converging_safe_zones"]
    world = MockWorld()
    mode.setup(world, [])

    assert mode.center_x == 500.0
    assert mode.center_y == 500.0
    assert len(mode.zones) == 4

    corners_x = [z["x"] for z in mode.zones]
    corners_y = [z["y"] for z in mode.zones]

    assert 200.0 in corners_x
    assert 800.0 in corners_x
    assert 200.0 in corners_y
    assert 800.0 in corners_y

def test_converging_safe_zones_movement():
    mode = GAME_MODES["converging_safe_zones"]
    world = MockWorld()
    mode.setup(world, [])

    initial_x = mode.zones[0]["x"]
    initial_y = mode.zones[0]["y"]

    mode.tick(world, [], delta=1.0)

    assert mode.zones[0]["x"] > initial_x
    assert mode.zones[0]["y"] > initial_y

def test_converging_safe_zones_player_damage():
    mode = GAME_MODES["converging_safe_zones"]
    world = MockWorld()

    ball_safe = MockBall(x=200.0, y=200.0, hp=100.0)
    ball_safe.id = 1
    ball_danger = MockBall(x=500.0, y=500.0, hp=100.0)
    ball_danger.id = 2

    mode.setup(world, [ball_safe, ball_danger])
    mode.tick(world, [ball_safe, ball_danger], delta=1.0)

    assert ball_safe.hp == 100.0
    assert ball_danger.hp == 75.0

def test_converging_safe_zones_weather_immunity():
    mode = GAME_MODES["converging_safe_zones"]
    world = MockWorld()

    ball_immune = MockBall(x=500.0, y=500.0, hp=100.0)
    ball_immune.id = 1

    mode.setup(world, [ball_immune])
    ball_immune.weather_immunity_timer = 5.0
    mode.tick(world, [ball_immune], delta=1.0)

    assert ball_immune.hp == 100.0
