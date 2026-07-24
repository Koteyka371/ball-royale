import pytest
from ai.game_modes import GameMode
from arena.arena_types import ProceduralArena
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena()
        self.dead_balls = []
        self.match_time = 0.0

class MockBall:
    def __init__(self, hp=100.0, speed=100.0, damage=10.0, traits=None, ball_type="base", cosmetic=""):
        self.ball_type = ball_type
        self.cosmetic = cosmetic
        self.alive = True
        self.weather_immunity_timer = 0.0
        self.max_hp = hp
        self.hp = hp
        self.base_speed = speed
        self.speed = speed
        self.base_damage = damage
        self.damage = damage
        self.traits = traits or []
        self.internal_temperature = 20.0
        self.x = 10.0
        self.y = 10.0

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius

class MockTraitsMode(GameMode):
    def setup(self, world, balls):
        pass

def test_ice_elemental_blizzard_buff():
    mode = MockTraitsMode()
    mode.weather = "blizzard"
    world = MockWorld()
    b = MockBall(cosmetic="ice_elemental")
    b.hp = 90.0
    mode.apply_dynamic_traits(world, [b], 1.0)
    assert b.speed == 120.0 # 100 * 1.2
    assert b.hp == 92.0 # 90 + 2.0
    assert b.weather_immunity_timer == 2.0

def test_ice_elemental_heatwave_debuff():
    mode = MockTraitsMode()
    mode.weather = "heatwave"
    world = MockWorld()
    b = MockBall(cosmetic="ice_elemental")
    mode.apply_dynamic_traits(world, [b], 1.0)
    assert b.speed == 80.0 # 100 * 0.8

def test_ice_elemental_ice_patch_buff():
    mode = MockTraitsMode()
    world = MockWorld()
    h = MockHazard("ice_patch", 10.0, 10.0, 50.0)
    world.arena.hazards = [h]

    b = MockBall(cosmetic="ice_elemental")
    mode.apply_dynamic_traits(world, [b], 1.0)

    assert b.speed == 150.0 # 100 * 1.5

def test_normal_ball_ice_patch():
    mode = MockTraitsMode()
    world = MockWorld()
    h = MockHazard("ice_patch", 10.0, 10.0, 50.0)
    world.arena.hazards = [h]

    b = MockBall() # Normal ball
    mode.apply_dynamic_traits(world, [b], 1.0)

    # Internal temp will drop because it's on an ice patch
    assert b.internal_temperature < 20.0
