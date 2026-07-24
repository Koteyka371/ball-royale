import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.game_modes import DayNightMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.is_night = False
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.max_hp = 100.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "normal"
        self.radius = 15.0
        self.flare_hp_penalty = 0.0

def test_solar_flare_out_of_cover():
    mode = DayNightMode()
    world = MockWorld()

    b1 = MockBall(1, 100, 100) # out of cover
    balls = [b1]

    mode.setup(world, balls)
    mode.is_solar_flare = True
    mode.solar_flare_timer = 5.0

    # Tick for 1 second (10 * 0.1 delta)
    for _ in range(10):
        mode.tick(world, balls, 0.1)

    assert b1.flare_hp_penalty > 0
    assert b1.max_hp < 100.0
    assert b1.hp == b1.max_hp

def test_solar_flare_in_cover():
    mode = DayNightMode()
    world = MockWorld()

    b1 = MockBall(1, 100, 100) # in cover
    balls = [b1]

    # Add cover hazard right on top of ball
    world.arena.hazards.append({"kind": "tree", "x": 100, "y": 100, "radius": 30.0})

    mode.setup(world, balls)
    mode.is_solar_flare = True
    mode.solar_flare_timer = 5.0

    # Tick for 1 second
    for _ in range(10):
        mode.tick(world, balls, 0.1)

    assert b1.flare_hp_penalty == 0
    assert b1.max_hp == 100.0

def test_solar_flare_recovery():
    mode = DayNightMode()
    world = MockWorld()

    b1 = MockBall(1, 100, 100)
    balls = [b1]

    mode.setup(world, balls)
    mode.is_solar_flare = True
    mode.solar_flare_timer = 1.0 # Will end quickly

    # Give some penalty
    for _ in range(5):
        mode.tick(world, balls, 0.1)

    assert b1.flare_hp_penalty > 0

    # Let the flare end and recover
    for _ in range(15): # Next ticks should bring it down
        mode.tick(world, balls, 0.1)

    # Recovery is fast enough that it should be 0 again
    assert b1.flare_hp_penalty == 0
    assert b1.max_hp == 100.0
