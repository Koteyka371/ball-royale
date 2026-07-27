import pytest
from ai.echolocation_only import EcholocationOnlyMode
from typing import Any, List

class MockArena:
    def __init__(self):
        self.is_night = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type: str, data: dict):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self):
        self.id = id(self)
        self.ball_type = "player"
        self.alive = True
        self.perception_radius = 100.0

def test_echolocation_only_mode():
    mode = EcholocationOnlyMode()
    world = MockWorld()
    b1 = MockBall()
    b2 = MockBall()
    balls = [b1, b2]

    mode.setup(world, balls)
    assert world.arena.is_night == True
    assert b1.perception_radius == 15.0
    assert b1.base_perception_radius == 100.0

    mode.tick(world, balls, 1.0)
    assert b1.perception_radius == 15.0
    assert not mode.is_pulsing

    mode.tick(world, balls, 3.1)
    assert mode.is_pulsing
    assert b1.perception_radius == 100.0
    assert len(world.events) == 1
    assert world.events[0][0] == "sound_pulse"

    mode.tick(world, balls, 0.6)
    assert not mode.is_pulsing
    assert b1.perception_radius == 15.0
