import pytest
from unittest.mock import MagicMock
from ai.game_modes import GhostTetherMode

class MockWorld:
    def __init__(self):
        self.arena = MagicMock()
        self.arena.width = 1000
        self.arena.height = 1000
        self.arena.hazards = []
        self.dead_balls = []
        self.events = []
    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id, alive=True):
        self.id = id
        self.alive = alive
        self.x = 500
        self.y = 500
        self.radius = 10
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.ball_type = "player"
        self.killer = -1
        self.is_ghost = False
        self.vx = 0
        self.vy = 0

def test_ghost_conversion():
    mode = GhostTetherMode()
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    b1.hp = 0
    b1.killer = 2
    world.dead_balls.append(1)

    balls = [b1, b2]
    mode.setup(world, balls)
    mode.tick(world, balls, 0.016)

    assert getattr(b1, "is_ghost", False) == True
    assert b1.hp == 50.0
    assert b1.max_hp == 50.0
    assert b1.damage == 5.0
    assert b1.alive == True
    assert 1 not in world.dead_balls
    assert mode.ghosts[1]["killer_id"] == 2

def test_tether_pull():
    mode = GhostTetherMode()
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    b1.is_ghost = True
    b1.x, b1.y = 100, 100
    b2.x, b2.y = 600, 600 # Dist > 300

    mode.setup(world, [b1, b2])
    mode.ghosts[1] = {"killer_id": 2, "chip_damage": 0, "orig_max_hp": 100, "orig_damage": 10}

    mode.tick(world, [b1, b2], 0.016)

    # Check that velocity is non-zero
    assert b1.vx != 0
    assert b1.vy != 0

def test_revive_chip_damage():
    mode = GhostTetherMode()
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    b1.is_ghost = True

    # B1 (ghost) and B2 (enemy) close to each other
    b1.x, b1.y = 500, 500
    b2.x, b2.y = 510, 510

    mode.setup(world, [b1, b2])
    mode.ghosts[1] = {"killer_id": -1, "chip_damage": 90, "orig_max_hp": 100, "orig_damage": 10}

    # Store initial HP for tracking
    mode.tick(world, [b1, b2], 0.016)

    # B2 takes 20 damage, pushing chip_damage over 100
    b2.hp = 80
    mode.tick(world, [b1, b2], 0.016)

    assert getattr(b1, "is_ghost", True) == False
    assert b1.hp == 100.0
    assert b1.damage == 10.0
    assert 1 not in mode.ghosts

def test_revive_assist():
    mode = GhostTetherMode()
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    b3 = MockBall(3)
    b1.is_ghost = True

    mode.setup(world, [b1, b2, b3])
    mode.ghosts[1] = {"killer_id": 2, "chip_damage": 0, "orig_max_hp": 100, "orig_damage": 10}

    # Tick 1: normal state
    mode.tick(world, [b1, b2, b3], 0.016)

    # Tick 2: b3 dies, killed by b2
    b3.hp = 0
    b3.alive = False
    b3.killer = 2

    mode.tick(world, [b1, b2, b3], 0.016)

    # b1 should revive
    assert getattr(b1, "is_ghost", True) == False
    assert b1.hp == 100.0
    assert b1.damage == 10.0
