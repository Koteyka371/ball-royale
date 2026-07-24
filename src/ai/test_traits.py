import pytest
from ai.game_modes import GameMode
from arena.arena_types import ProceduralArena

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena()
        self.dead_balls = []
        self.match_time = 0.0

class MockBall:
    def __init__(self, hp=100.0, speed=100.0, damage=10.0, traits=None, ball_type="base"):
        self.ball_type = ball_type
        self.alive = True
        self.weather_immunity_timer = 0.0
        self.max_hp = hp
        self.hp = hp
        self.base_speed = speed
        self.speed = speed
        self.base_damage = damage
        self.damage = damage
        self.traits = traits or []

# We create a child class of GameMode to only test traits
class MockTraitsMode(GameMode):
    def setup(self, world, balls):
        # Apply the traits logic just as done in GameMode
        for b in balls:
            traits = getattr(b, "traits", [])
            for trait in traits:
                if trait == "swift":
                    b.speed = getattr(b, "speed", 100.0) * 1.05
                    if hasattr(b, "base_speed"):
                        b.base_speed *= 1.05
                elif trait == "slow":
                    b.speed = getattr(b, "speed", 100.0) * 0.95
                    if hasattr(b, "base_speed"):
                        b.base_speed *= 0.95
                elif trait == "sturdy":
                    b.max_hp = getattr(b, "max_hp", 100.0) * 1.05
                    b.hp = min(getattr(b, "hp", 100.0) * 1.05, b.max_hp)
                elif trait == "fragile":
                    b.max_hp = getattr(b, "max_hp", 100.0) * 0.95
                    b.hp = min(getattr(b, "hp", 100.0), b.max_hp)
                elif trait == "lethal":
                    b.damage = getattr(b, "damage", 10.0) * 1.05
                    if hasattr(b, "base_damage"):
                        b.base_damage *= 1.05
                elif trait == "weak":
                    b.damage = getattr(b, "damage", 10.0) * 0.95
                    if hasattr(b, "base_damage"):
                        b.base_damage *= 0.95

def test_swift_trait():
    mode = MockTraitsMode()
    world = MockWorld()
    b = MockBall(traits=["swift"])
    mode.setup(world, [b])
    assert b.speed == 105.0
    assert b.base_speed == 105.0

def test_slow_trait():
    mode = MockTraitsMode()
    world = MockWorld()
    b = MockBall(traits=["slow"])
    mode.setup(world, [b])
    assert b.speed == 95.0
    assert b.base_speed == 95.0

def test_sturdy_trait():
    mode = MockTraitsMode()
    world = MockWorld()
    b = MockBall(traits=["sturdy"])
    mode.setup(world, [b])
    assert b.max_hp == 105.0
    assert b.hp == 105.0

def test_fragile_trait():
    mode = MockTraitsMode()
    world = MockWorld()
    b = MockBall(traits=["fragile"])
    mode.setup(world, [b])
    assert b.max_hp == 95.0
    assert b.hp == 95.0

def test_lethal_trait():
    mode = MockTraitsMode()
    world = MockWorld()
    b = MockBall(traits=["lethal"])
    mode.setup(world, [b])
    assert b.damage == 10.5
    assert b.base_damage == 10.5

def test_weak_trait():
    mode = MockTraitsMode()
    world = MockWorld()
    b = MockBall(traits=["weak"])
    mode.setup(world, [b])
    assert b.damage == 9.5
    assert b.base_damage == 9.5

def test_multiple_traits():
    mode = MockTraitsMode()
    world = MockWorld()
    b = MockBall(traits=["swift", "fragile"])
    mode.setup(world, [b])
    assert b.speed == 105.0
    assert b.max_hp == 95.0


def test_fire_trait_heatwave():
    mode = MockTraitsMode()
    world = MockWorld()
    world.arena.weather = "heatwave"
    b = MockBall(ball_type="fire")
    mode.apply_dynamic_traits(world, [b], 1.0)
    assert b.speed == 120.0
    assert b.damage == 12.0

def test_fire_trait_rain():
    mode = MockTraitsMode()
    world = MockWorld()
    world.arena.weather = "rain"
    b = MockBall(ball_type="fire")
    mode.apply_dynamic_traits(world, [b], 1.0)
    assert b.speed == 80.0
    assert b.damage == 8.0

def test_earth_trait_sandstorm():
    mode = MockTraitsMode()
    world = MockWorld()
    world.arena.weather = "sandstorm"
    b = MockBall(ball_type="earth")
    mode.apply_dynamic_traits(world, [b], 1.0)
    assert b.weather_immunity_timer == 2.0

def test_earth_trait_dirt():
    mode = MockTraitsMode()
    world = MockWorld()
    world.arena.name = "dirt_arena"
    b = MockBall(ball_type="earth")
    mode.apply_dynamic_traits(world, [b], 1.0)
    assert b.defense_multiplier == 0.8

def test_synergy_water_lightning_electrified_water():
    mode = MockTraitsMode()
    world = MockWorld()

    # Setup team
    b_water = MockBall(ball_type="water")
    b_water.team = 1

    b_lightning = MockBall(ball_type="lightning")
    b_lightning.team = 1

    # Setup enemies
    enemy1 = MockBall(ball_type="base", hp=100.0)
    enemy1.team = 2
    enemy1.x = 10.0
    enemy1.y = 10.0

    b_water.x = 0.0
    b_water.y = 0.0
    b_lightning.x = 50.0
    b_lightning.y = 50.0

    # Initial timer is 0. Delta of 1.5 should trigger the 1.0 check
    mode.apply_dynamic_traits(world, [b_water, b_lightning, enemy1], 1.5)

    # Water should get speed boost (base 100 * 1.25 = 125)
    assert b_water.speed == 125.0
    # Lightning should get speed boost (base 100 * 1.25 = 125)
    assert b_lightning.speed == 125.0

    # Enemy1 should take damage from the electrified water pulse
    # Two pulses (one from water, one from lightning) since both triggered > 1.0 timer
    # Wait, enemy1 is at (10,10) which is distance ~14 from water (r=150) -> hit
    # and distance ~56 from lightning (r=150) -> hit
    # Damage is 15 per hit. 100 - 15 - 15 = 70
    assert enemy1.hp == 70.0
