import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x=500.0, y=500.0, alive=True):
        self.id = id(self)
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = alive
        self.base_speed = 100.0
        self.base_damage = 10.0
        self.speed = 100.0
        self.damage = 10.0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

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

def test_biome_safe_zones_exist():
    assert "biome_safe_zones" in GAME_MODES

def test_biome_safe_zones_outside_damage():
    mode = GAME_MODES["biome_safe_zones"]
    world = MockWorld()
    b = MockBall(x=5000.0, y=5000.0) # Far away
    balls = [b]

    mode.setup(world, balls)
    mode.tick(world, balls, 1.0)

    assert b.hp < 100.0

def test_biome_safe_zones_fire_buff():
    mode = GAME_MODES["biome_safe_zones"]
    world = MockWorld()
    b = MockBall(x=500.0, y=500.0)
    balls = [b]

    mode.setup(world, balls)

    # Force first zone to be fire and cover the ball
    mode.zones[0]["biome"] = "fire"
    mode.zones[0]["x"] = 500.0
    mode.zones[0]["y"] = 500.0
    mode.zones[0]["radius"] = 1000.0

    # Remove others for isolated test
    mode.zones = [mode.zones[0]]

    mode.tick(world, balls, 1.0)
    assert b.hp == 100.0 # No damage taken inside
    assert b.damage > b.base_damage # Damage buff applied

def test_biome_safe_zones_ice_buff():
    mode = GAME_MODES["biome_safe_zones"]
    world = MockWorld()
    b = MockBall(x=500.0, y=500.0)
    balls = [b]

    mode.setup(world, balls)

    mode.zones[0]["biome"] = "ice"
    mode.zones[0]["x"] = 500.0
    mode.zones[0]["y"] = 500.0
    mode.zones[0]["radius"] = 1000.0
    mode.zones = [mode.zones[0]]

    mode.tick(world, balls, 1.0)
    assert getattr(b, "energy_shield_active", False) == True

def test_biome_safe_zones_nature_buff():
    mode = GAME_MODES["biome_safe_zones"]
    world = MockWorld()
    b = MockBall(x=500.0, y=500.0)
    b.hp = 50.0 # damaged
    balls = [b]

    mode.setup(world, balls)

    mode.zones[0]["biome"] = "nature"
    mode.zones[0]["x"] = 500.0
    mode.zones[0]["y"] = 500.0
    mode.zones[0]["radius"] = 1000.0
    mode.zones = [mode.zones[0]]

    mode.tick(world, balls, 1.0)
    assert b.hp > 50.0

def test_biome_safe_zones_void_buff():
    mode = GAME_MODES["biome_safe_zones"]
    world = MockWorld()
    b = MockBall(x=500.0, y=500.0)
    balls = [b]

    mode.setup(world, balls)

    mode.zones[0]["biome"] = "void"
    mode.zones[0]["x"] = 500.0
    mode.zones[0]["y"] = 500.0
    mode.zones[0]["radius"] = 1000.0
    mode.zones = [mode.zones[0]]

    mode.tick(world, balls, 1.0)
    assert b.speed > b.base_speed
    assert b.hp < 100.0 # Takes void damage
