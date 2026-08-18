import pytest
import math
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x=0, y=0, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 15.0
        self.quantum_teleport_cooldown = 0.0
        self.hp = 100
        self.alive = True

def test_quantum_detonators_spawn():
    mode = GAME_MODES["quantum_detonators"]
    world = type('MockWorld', (), {})()
    world.arena = type('MockArena', (), {'width': 1000, 'height': 1000})()

    # Mock random to force spawn
    import random
    original_random = random.random
    random.random = lambda: 0.0001

    mode.setup(world, [])

    # Tick to spawn detonator
    mode.tick(world, [], delta=1.0)

    assert len(world.quantum_detonators) > 0
    assert world.quantum_detonators[-1]["timer"] == 2.0
    random.random = original_random

def test_quantum_detonators_explosion():
    mode = GAME_MODES["quantum_detonators"]
    world = type('MockWorld', (), {})()
    world.arena = type('MockArena', (), {'width': 1000, 'height': 1000})()

    # Mock random to avoid random spawns during tick
    import random
    original_random = random.random
    random.random = lambda: 0.5

    mode.setup(world, [])

    # Add a detonator with timer 0.1
    world.quantum_detonators.append({
        "x": 100,
        "y": 100,
        "timer": 0.1,
        "radius": 30.0
    })

    # Tick past the timer
    mode.tick(world, [], delta=0.2)

    assert len(world.quantum_detonators) == 0
    assert len(world.chaotic_zones) == 1
    assert world.chaotic_zones[0]["x"] == 100
    assert world.chaotic_zones[0]["y"] == 100
    assert world.chaotic_zones[0]["duration"] == 5.0 - 0.2
    random.random = original_random

def test_quantum_detonators_teleport():
    mode = GAME_MODES["quantum_detonators"]
    world = type('MockWorld', (), {})()
    world.arena = type('MockArena', (), {'width': 1000, 'height': 1000})()

    # Mock random to avoid random spawns and control choice
    import random
    original_random = random.random
    random.random = lambda: 0.5

    mode.setup(world, [])

    # Add two zones
    world.chaotic_zones = [
        {"x": 100, "y": 100, "radius": 60.0, "duration": 5.0},
        {"x": 500, "y": 500, "radius": 60.0, "duration": 5.0}
    ]

    # Create ball moving towards zone 1
    ball = MockBall(x=100, y=100, vx=50, vy=-50)

    def mock_choice(seq):
        return world.chaotic_zones[1]

    import random
    original_choice = random.choice
    random.choice = mock_choice

    mode.tick(world, [ball], delta=0.1)

    # Check teleportation and velocity reversal
    assert ball.x == 500
    assert ball.y == 500
    assert ball.vx == -50
    assert ball.vy == 50
    assert ball.quantum_teleport_cooldown == 1.0
    random.random = original_random
    random.choice = original_choice
