import pytest
from src.ai.lava_eruption import LavaEruptionEventMode
from typing import Any

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.weather_immunity_timer = 0.0

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

    def has_method(self, name):
        return hasattr(self, name)

def test_lava_eruption_event():
    mode = LavaEruptionEventMode()
    world = MockWorld()
    balls = [MockBall(1, 400.0, 400.0)]

    # Fast forward just before eruption
    mode.apply_dynamic_traits(world, balls, 7.9)
    assert len(mode.eruptions) == 0
    assert len(mode.puddles) == 0

    # Trigger eruption spawning
    mode.apply_dynamic_traits(world, balls, 0.2)
    assert len(mode.eruptions) > 0
    assert len(mode.puddles) == 0

    # Overwrite one eruption's coordinates to be directly on the ball
    mode.eruptions[0]["x"] = 400.0
    mode.eruptions[0]["y"] = 400.0

    # Process warning phase and convert to puddle
    mode.apply_dynamic_traits(world, balls, 2.1)

    # Check that at least one puddle spawned
    assert len(mode.puddles) > 0

    # Check damage and burn timer on ball
    assert balls[0].hp < 100.0
    assert getattr(balls[0], "burn_timer", 0.0) > 0.0
