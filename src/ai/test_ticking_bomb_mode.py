import pytest
from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES

def test_ticking_bomb_mode_spawn():
    mode = GAME_MODES["ticking_bomb"]
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.hazards = []

    # Tick below interval
    mode.tick(world, [], delta=5.0)
    assert len(world.arena.hazards) == 0

    # Tick past interval but with a small delta so the bomb doesn't immediately explode
    mode.spawn_timer = 9.9
    mode.tick(world, [], delta=0.2)
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "ticking_bomb"
    assert world.arena.hazards[0].active is True

def test_ticking_bomb_mode_explosion():
    mode = GAME_MODES["ticking_bomb"]
    world = MagicMock()
    world.arena = MagicMock()

    class _MockHazard:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.kind = "ticking_bomb"
            self.active = True
            self.duration = 0.5
            self.radius = 30.0

    bomb = _MockHazard(500, 500)
    world.arena.hazards = [bomb]

    class _MockBall:
        def __init__(self, id, x, y):
            self.id = id
            self.x = x
            self.y = y
            self.alive = True
            self.hp = 100.0

    b1 = _MockBall(1, 500, 500) # In radius
    b2 = _MockBall(2, 900, 900) # Out of radius
    balls = [b1, b2]

    mode.tick(world, balls, delta=0.6)

    # Bomb should be removed, explosion hazard spawned
    assert bomb not in world.arena.hazards
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "explosion"

    # b1 should take 50 damage, b2 should take 0
    assert b1.hp == 50.0
    assert b1.alive is True
    assert b2.hp == 100.0

def test_ticking_bomb_mode_death():
    mode = GAME_MODES["ticking_bomb"]
    world = MagicMock()
    world.arena = MagicMock()
    world.dead_balls = []

    class _MockHazard:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.kind = "ticking_bomb"
            self.active = True
            self.duration = 0.1
            self.radius = 30.0

    bomb = _MockHazard(500, 500)
    world.arena.hazards = [bomb]

    class _MockBall:
        def __init__(self, id, x, y):
            self.id = id
            self.x = x
            self.y = y
            self.alive = True
            self.hp = 30.0

    b1 = _MockBall(1, 500, 500)

    mode.tick(world, [b1], delta=0.2)

    assert b1.hp == 0.0
    assert b1.alive is False
    assert b1.id in world.dead_balls
