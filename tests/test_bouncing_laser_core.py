import pytest
import math
from ai.bouncing_laser_core import BouncingLaserCoreMode

class MockArena:
    def __init__(self):
        self.width = 800.0
        self.height = 600.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "player"

def test_bouncing_laser_core_setup():
    mode = BouncingLaserCoreMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)

    assert len(world.arena.hazards) == 1
    core = world.arena.hazards[0]
    assert core.kind == "bouncing_laser_core"
    assert core.x == 400.0
    assert core.y == 300.0
    assert hasattr(core, "vx")
    assert hasattr(core, "vy")
    assert core.angle == 0.0

def test_bouncing_laser_core_tick():
    mode = BouncingLaserCoreMode()
    world = MockWorld()

    # Manually setup hazard
    from arena.procedural_arena import Hazard
    core = Hazard(id=1576, x=400.0, y=300.0, radius=30.0, kind="bouncing_laser_core", damage=0.0)
    core.vx = 100.0
    core.vy = 0.0
    core.angle = 0.0
    core.rotation_speed = 1.0
    world.arena.hazards.append(core)

    # Place a ball in the beam path (beam is horizontal at angle 0)
    ball = MockBall(500.0, 300.0)

    delta = 0.1
    mode.tick(world, [ball], delta)

    # Core should move
    assert core.x == 410.0
    assert core.y == 300.0

    # Angle should change
    assert core.angle == 0.1

    # Ball should take damage (laser_damage_per_second * delta)
    assert ball.hp < 100.0

def test_bouncing_laser_core_bounce():
    mode = BouncingLaserCoreMode()
    world = MockWorld()

    # Put hazard near right wall
    from arena.procedural_arena import Hazard
    core = Hazard(id=1576, x=740.0, y=300.0, radius=30.0, kind="bouncing_laser_core", damage=0.0)
    core.vx = 100.0
    core.vy = 0.0
    core.angle = 0.0
    core.rotation_speed = 1.0
    world.arena.hazards.append(core)

    delta = 1.0 # Moves 100 pixels, crossing the wall (750 is max due to 800 - 50)
    mode.tick(world, [], delta)

    # Hazard should bounce back
    assert core.vx < 0.0
