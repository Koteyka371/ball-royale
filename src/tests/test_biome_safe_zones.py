import pytest
from ai.game_modes import GAME_MODES

def test_biome_safe_zones_exist():
    assert "biome_safe_zones" in GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, type_name, data):
        self.events.append((type_name, data))

class MockBall:
    def __init__(self, x, y, hp=100, max_hp=200, shield=0, damage_multiplier=1.0, speed_multiplier=1.0, alive=True):
        self.id = 1
        self.x = x
        self.y = y
        self.alive = alive
        self.hp = hp
        self.max_hp = max_hp
        self.shield = shield
        self.damage_multiplier = damage_multiplier
        self.speed_multiplier = speed_multiplier
        self.weather_immunity_timer = 0.0
        self.ball_type = "base"

def test_biome_safe_zones_mode():
    mode = GAME_MODES["biome_safe_zones"]
    world = MockWorld()

    b_fire = MockBall(500, 500)

    balls = [b_fire]

    mode.setup(world, balls)

    assert len(mode.zones) == 1

    mode.zones[0]["biome"] = "fire"
    mode.zones[0]["x"] = 500
    mode.zones[0]["y"] = 500
    mode.zones[0]["radius"] = 100

    initial_dmg = b_fire.damage_multiplier
    mode.tick(world, balls, 1.0)
    assert b_fire.damage_multiplier > initial_dmg

    mode.zones[0]["biome"] = "ice"
    initial_shield = b_fire.shield
    mode.tick(world, balls, 1.0)
    assert b_fire.shield > initial_shield

    mode.zones[0]["biome"] = "nature"
    initial_hp = b_fire.hp
    mode.tick(world, balls, 1.0)
    assert b_fire.hp > initial_hp

    mode.zones[0]["biome"] = "wind"
    initial_speed = b_fire.speed_multiplier
    mode.tick(world, balls, 1.0)
    assert b_fire.speed_multiplier > initial_speed
