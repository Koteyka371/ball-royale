import pytest
import math
import random
from unittest.mock import MagicMock
from ai.game_modes import SacrificeAltarMode

class MockBall:
    def __init__(self, id, x=0.0, y=0.0):
        self.id = id
        self.alive = True
        self.x = x
        self.y = y
        self.radius = 10.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.base_damage = 10.0
        self.damage = 10.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.sacrifice_cooldown = 0.0

def _setup_world():
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.width = 1000.0
    world.arena.height = 1000.0
    world.add_event = MagicMock()
    world.boosters = []
    return world

def test_sacrifice_altar_buff():
    mode = SacrificeAltarMode()
    world = _setup_world()

    ball = MockBall(1, x=100.0, y=100.0)
    world.sacrifice_altars = [{"x": 100.0, "y": 100.0, "radius": 60.0}]

    with pytest.MonkeyPatch().context() as m:
        m.setattr(random, 'random', lambda: 0.1) # Force buff ( < 0.5 )
        mode.tick(world, [ball], 0.016)

    assert ball.max_hp == 70.0
    assert ball.hp == 70.0
    assert ball.sacrifice_cooldown == 15.0
    assert ball.base_damage == 15.0
    assert ball.damage == 15.0
    assert ball.base_speed == 150.0
    assert ball.speed == 150.0
    world.add_event.assert_called_once()

def test_sacrifice_altar_booster_spawn():
    mode = SacrificeAltarMode()
    world = _setup_world()

    ball = MockBall(1, x=100.0, y=100.0)
    world.sacrifice_altars = [{"x": 100.0, "y": 100.0, "radius": 60.0}]

    with pytest.MonkeyPatch().context() as m:
        m.setattr(random, 'random', lambda: 0.9) # Force booster ( >= 0.5 )
        m.setattr(random, 'choice', lambda x: "overclock_booster")
        mode.tick(world, [ball], 0.016)

    assert ball.max_hp == 70.0
    assert ball.hp == 70.0
    assert ball.sacrifice_cooldown == 15.0
    assert ball.base_damage == 10.0 # Unchanged
    assert len(world.boosters) == 1
    assert world.boosters[0]["kind"] == "overclock_booster"
    world.add_event.assert_called_once()

def test_sacrifice_altar_cooldown():
    mode = SacrificeAltarMode()
    world = _setup_world()

    ball = MockBall(1, x=100.0, y=100.0)
    ball.sacrifice_cooldown = 10.0
    world.sacrifice_altars = [{"x": 100.0, "y": 100.0, "radius": 60.0}]

    mode.tick(world, [ball], 0.016)

    assert ball.max_hp == 100.0 # Did not trigger
    assert ball.sacrifice_cooldown == 10.0 - 0.016
    world.add_event.assert_not_called()
