import math
import pytest
from ai.game_modes import GameMode, GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y, hp):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "normal"
        self.base_speed = 100.0
        self._base_speed_set = True
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self.corrupted_buff = False

def test_corrupted_zones():
    mode = GAME_MODES.get("corrupted_zones")
    assert mode is not None

    world = MockWorld()
    b1 = MockBall(1, 100, 100, 100)
    b2 = MockBall(2, 500, 500, 100)
    balls = [b1, b2]

    mode.setup(world, balls)
    assert len(mode.zones) == 0

    # Fast forward to spawn zone
    mode.spawn_timer = 15.0
    mode.tick(world, balls, delta=0.016)
    assert len(mode.zones) == 1

    zone = mode.zones[0]
    # Move b1 into zone
    b1.x = zone["x"]
    b1.y = zone["y"]

    # Move b2 far away
    b2.x = zone["x"] + 1000
    b2.y = zone["y"] + 1000

    mode.tick(world, balls, delta=1.0)

    # b1 should have taken damage and gotten buffed
    assert b1.hp < 100
    assert getattr(b1, "speed_multiplier", 1.0) == 2.0
    assert getattr(b1, "damage_multiplier", 1.0) == 2.5
    assert getattr(b1, "corrupted_buff", False) == True

    # b2 should be untouched
    assert b2.hp >= 99.0
    assert getattr(b2, "speed_multiplier", 1.0) == 1.0
    assert getattr(b2, "damage_multiplier", 1.0) == 1.0
    assert getattr(b2, "corrupted_buff", False) == False

    # Move b1 out of zone
    b1.x = zone["x"] + 1000
    b1.y = zone["y"] + 1000

    mode.tick(world, balls, delta=1.0)

    # b1 buff should be removed
    assert getattr(b1, "speed_multiplier", 1.0) == 1.0
    assert getattr(b1, "damage_multiplier", 1.0) == 1.0
    assert getattr(b1, "corrupted_buff", False) == False
