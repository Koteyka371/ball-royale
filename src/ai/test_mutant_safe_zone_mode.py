import pytest
import math
from ai.game_modes import MutantSafeZoneMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100
        self.ball_type = "player"
        self.team = "team1"
        self.base_speed = 100.0
        self.base_damage_multiplier = 1.0
        self.base_perception_radius = 150.0

def test_mutant_safe_zone_initialization():
    mode = MutantSafeZoneMode()
    assert mode.name == "Mutant Safe Zone"
    assert "mutations" in mode.description.lower()

def test_mutant_safe_zone_tick_inside_zone():
    mode = MutantSafeZoneMode()
    world = MockWorld()

    # Ball inside the safe zone (center is 500, 500)
    b1 = MockBall(500, 500)
    mode.setup(world, [b1])

    initial_speed = b1.base_speed
    initial_damage = b1.base_damage_multiplier
    initial_perception = b1.base_perception_radius

    # Set high probability for testing (won't trigger inside)
    # Actually random chance is handled inside tick
    mode.tick(world, [b1], delta=100.0) # huge delta to trigger probability if it was outside

    assert b1.hp == 100 # No damage taken
    assert b1.base_speed == initial_speed
    assert b1.base_damage_multiplier == initial_damage
    assert b1.base_perception_radius == initial_perception

def test_mutant_safe_zone_tick_outside_zone(monkeypatch):
    mode = MutantSafeZoneMode()
    world = MockWorld()

    # Ball far outside the safe zone
    b1 = MockBall(0, 0)
    mode.setup(world, [b1])

    import random

    # Force the random logic to always apply mutation
    monkeypatch.setattr(random, 'random', lambda: 0.0)
    monkeypatch.setattr(random, 'choice', lambda seq: "speed")
    monkeypatch.setattr(random, 'uniform', lambda a, b: 1.5)

    initial_speed = b1.base_speed
    mode.tick(world, [b1], delta=1.0)

    # It should have taken damage
    assert b1.hp < 100

    # And mutated base speed
    assert b1.base_speed == initial_speed * 1.5
    assert b1.base_damage_multiplier == 1.0

    # Test damage mutation
    monkeypatch.setattr(random, 'choice', lambda seq: "damage")
    monkeypatch.setattr(random, 'uniform', lambda a, b: 0.5)

    initial_damage = b1.base_damage_multiplier
    speed_before = b1.base_speed
    mode.tick(world, [b1], delta=1.0)
    assert b1.base_damage_multiplier == initial_damage * 0.5
    assert b1.base_speed == speed_before

    # Test perception mutation
    monkeypatch.setattr(random, 'choice', lambda seq: "perception")
    monkeypatch.setattr(random, 'uniform', lambda a, b: 2.0)

    initial_perception = b1.base_perception_radius
    mode.tick(world, [b1], delta=1.0)
    assert b1.base_perception_radius == initial_perception * 2.0
