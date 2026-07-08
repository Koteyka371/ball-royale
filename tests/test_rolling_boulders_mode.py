import pytest
from unittest.mock import MagicMock
from ai.game_modes import RollingBouldersMode
import random

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100
        self.alive = True
        self.ball_type = "normal"
        self.radius = 15.0
        self.killer = ""

class MockHazard:
    def __init__(self, id, x, y, radius, kind, damage):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.vx = 0.0
        self.vy = 0.0

def test_rolling_boulder_spawn():
    mode = RollingBouldersMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager
    world.arena.hazards = []
    world.arena.width = 1000
    world.arena.height = 1000
    balls = []

    mode.setup(world, balls)

    mode.spawn_timer = 5.0
    mode.tick(world, balls, delta=0.1)


    # Verify a boulder was spawned
    assert len(world.arena.hazards) == 1
    boulder = world.arena.hazards[0]
    assert getattr(boulder, "kind", "") == "rolling_boulder"
    assert getattr(boulder, "radius", 0) == 60.0
    assert getattr(boulder, "damage", 0) == 300.0
    assert getattr(boulder, "vx", 0) != 0 or getattr(boulder, "vy", 0) != 0

def test_rolling_boulder_crush():
    mode = RollingBouldersMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager
    world.arena.hazards = []
    world.arena.width = 1000
    world.arena.height = 1000
    world.arena.walls = []

    ball = MockBall(500, 500)
    balls = [ball]

    mode.setup(world, balls)

    # Spawn a boulder artificially
    boulder = MockHazard(1, 500, 500, 60.0, "rolling_boulder", 300.0)
    boulder.vx = 0.0
    boulder.vy = 0.0
    world.arena.hazards.append(boulder)

    # Tick should trigger collision
    mode.tick(world, balls, delta=0.1)

    assert ball.hp == 0
    assert ball.alive == False
    assert ball.killer == "rolling_boulder"

def test_rolling_boulder_shatter():
    mode = RollingBouldersMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager
    world.arena.hazards = []
    world.arena.width = 1000
    world.arena.height = 1000
    world.arena.walls = []
    balls = []

    mode.setup(world, balls)

    # Spawn a boulder right next to the boundary
    boulder = MockHazard(1, -200, 500, 60.0, "rolling_boulder", 300.0)
    boulder.vx = -100.0
    boulder.vy = 0.0
    world.arena.hazards.append(boulder)

    # Tick should move it further out and shatter it
    mode.tick(world, balls, delta=0.1)

    # The original boulder should be gone, and 3 rocks should remain
    hazards = world.arena.hazards
    boulders = [h for h in hazards if getattr(h, "kind", "") == "rolling_boulder"]
    rocks = [h for h in hazards if getattr(h, "kind", "") == "rock"]

    assert len(boulders) == 0
    assert len(rocks) == 3
