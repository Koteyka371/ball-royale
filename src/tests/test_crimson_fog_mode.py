import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id):
        self.id = id
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = "A"
        self.x = 0.0
        self.y = 0.0

class MockArena:
    def __init__(self):
        self.is_foggy = False
        self.weather = "clear"
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

def test_crimson_fog_mode_toggles():
    mode = GAME_MODES["crimson_fog"]
    world = MockWorld()
    b1 = MockBall("b1")

    mode.setup(world, [b1])
    assert not mode.fog_active

    mode.tick(world, [b1], delta=20.0)
    assert mode.fog_active
    assert world.arena.is_foggy

def test_crimson_fog_mode_drain():
    mode = GAME_MODES["crimson_fog"]
    world = MockWorld()
    b1 = MockBall("b1")

    mode.setup(world, [b1])
    mode.tick(world, [b1], delta=20.0)
    assert mode.fog_active

    b1.hp = 100.0
    b1.alive = True
    hp_before = b1.hp
    mode.tick(world, [b1], delta=1.0)

    assert b1.hp < hp_before
    assert b1.hp == hp_before - 5.0

def test_crimson_fog_mode_lifesteal():
    mode = GAME_MODES["crimson_fog"]
    world = MockWorld()
    b1 = MockBall("b1")
    b2 = MockBall("b2")

    mode.setup(world, [b1, b2])
    mode.tick(world, [b1, b2], delta=20.0) # Fast forward to fog
    b1.hp = 50.0
    b2.hp = 100.0
    b1.alive = True
    b2.alive = True

    # Simulate b1 attacking b2
    b2._last_hit_by_id = b1.id
    b2._last_hit_by_timer = 2.0

    # Simulate damage being dealt BEFORE the tick
    # Wait, the tick will calculate last_hp - current_hp
    b2._crimson_fog_last_hp = 100.0
    b2.hp = 80.0

    hp_before_b1 = b1.hp
    mode.tick(world, [b1, b2], delta=1.0)

    # b1 should have healed 2 * damage_taken (2 * 20 = 40)
    # But b1 ALSO takes 5.0 damage from the fog during this tick!
    # So b1 HP = 50 + 40 - 5 = 85
    assert b1.hp == 85.0

    # Verify lifesteal event was fired
    assert any(e["type"] == "lifesteal_proc" for e in world.events)
