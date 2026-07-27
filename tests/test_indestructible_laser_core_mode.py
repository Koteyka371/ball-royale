import pytest
from ai.game_modes import IndestructibleLaserCoreMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

def test_indestructible_laser_core_mode_setup():
    mode = IndestructibleLaserCoreMode()
    world = MockWorld()
    mode.setup(world, [])
    assert mode.core_spawned == False
    assert len(world.arena.hazards) == 0

def test_indestructible_laser_core_mode_tick_spawn():
    mode = IndestructibleLaserCoreMode()
    world = MockWorld()
    mode.setup(world, [])

    mode.tick(world, [], 0.016)

    assert mode.core_spawned == True
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.id == "indestructible_laser_core_0"
    assert hazard.kind == "spinning_laser"
    assert hazard.radius == 500.0

    assert hazard.vx != 0 or hazard.vy != 0

def test_indestructible_laser_core_mode_tick_move_and_bounce():
    mode = IndestructibleLaserCoreMode()
    world = MockWorld()
    mode.setup(world, [])

    # Spawn the hazard
    mode.tick(world, [], 0.016)
    hazard = world.arena.hazards[0]

    # Force its position close to a wall and velocity towards it
    hazard.x = 10.0
    hazard.vx = -100.0
    hazard.core_radius = 40.0

    initial_vx = hazard.vx

    # Tick it
    mode.tick(world, [], 1.0)

    # It should hit the wall and reverse X velocity (with some potential random variation, but vx should now be positive)
    assert hazard.vx > 0
    assert hazard.x == hazard.core_radius
