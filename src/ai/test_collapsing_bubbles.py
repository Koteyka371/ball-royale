import math
import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, type_name, data):
        self.events.append((type_name, data))

class MockBall:
    def __init__(self, x, y, hp=100, alive=True):
        self.id = 1
        self.x = x
        self.y = y
        self.alive = alive
        self.hp = hp
        self.weather_immunity_timer = 0.0

def test_collapsing_bubbles_mode_setup():
    mode = GAME_MODES["collapsing_bubbles"]
    world = MockWorld()
    balls = []

    mode.setup(world, balls)

    assert len(mode.bubbles) == 5
    assert mode.bubble_spawn_timer == 0.0

def test_collapsing_bubbles_mode_damage():
    mode = GAME_MODES["collapsing_bubbles"]
    world = MockWorld()

    # Move ball far away so it's definitely not in a bubble
    b_outside = MockBall(-1000, -1000)

    mode.setup(world, [b_outside])

    # Tick to apply damage (outside)
    mode.tick(world, [b_outside], 1.0)

    assert b_outside.hp == 75.0 # Started at 100, took 25 damage

def test_collapsing_bubbles_mode_spawn_limit():
    mode = GAME_MODES["collapsing_bubbles"]
    world = MockWorld()

    mode.setup(world, [])

    # Force max bubbles
    mode.max_bubbles = 5
    mode.bubbles = [{"x": 500, "y": 500, "radius": 200, "timer": 10, "collapsing": False} for _ in range(5)]

    # Tick to spawn bubble
    mode.bubble_spawn_timer = 0.0
    mode.tick(world, [], 1.0)

    # Since max bubbles is 5, it should not have spawned more
    assert len(mode.bubbles) == 5
