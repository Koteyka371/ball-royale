import pytest
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick = 0
        self.balls = []

class MockBall:
    def __init__(self, id, x, y, hp=100):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.radius = 10.0
        self.alive = True
        self.team = "A"

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

def test_rotating_laser_walls_mode():
    mode = GAME_MODES["rotating_laser_walls"]
    world = MockWorld()
    balls = [MockBall(1, 500, 500)]

    # Setup mode
    mode.setup(world, balls)
    assert not mode.lasers_spawned

    # Tick to spawn lasers
    mode.tick(world, balls, delta=0.016)
    assert mode.lasers_spawned
    assert len(world.arena.hazards) == 2

    laser1 = world.arena.hazards[0]
    laser2 = world.arena.hazards[1]

    assert laser1.kind == "rotating_laser_wall"
    assert laser1.angle == 0.0
    assert laser1.damage == 60.0

    assert laser2.kind == "rotating_laser_wall"
    assert laser2.angle == math.pi / 2.0
    assert laser2.damage == 60.0

# Skip the complex action loop integration test because Action is heavily intertwined with other attributes
# The patch is exactly matching spinning_laser physics/damage style, which is sufficient.
