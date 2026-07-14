import pytest
from src.ai.game_modes import StatsDecayMode

class MockBall:
    def __init__(self):
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.damage = 10.0

class MockBooster:
    def __init__(self, kind):
        self.kind = kind
        self.active = True

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        self.boosters = []
        self.match_time = 0.0

def test_stats_decay_mode():
    mode = StatsDecayMode()
    world = MockWorld()
    b1 = MockBall()
    b2 = MockBall()
    balls = [b1, b2]

    # Setup
    mode.setup(world, balls)
    assert b1.max_hp == 200.0
    assert b1.hp == 200.0
    assert b1.base_speed == 200.0
    assert b1.speed == 200.0
    assert b1.base_damage == 20.0
    assert b1.damage == 20.0
    assert b1._original_decay_max_hp == 200.0
    assert b1._original_decay_speed == 200.0
    assert b1._original_decay_damage == 20.0

    # Tick at 0 time - stats should be mostly same
    mode.tick(world, balls, 0.0)
    assert b1.max_hp == 200.0
    assert b1.base_speed == 200.0
    assert b1.base_damage == 20.0

    # Tick at 30 seconds (halfway through decay)
    mode.tick(world, balls, 30.0)
    # total match time is 30, progress = 30/60 = 0.5
    # scale factor = 1.0 - (0.75 * 0.5) = 1.0 - 0.375 = 0.625
    # 200 * 0.625 = 125
    assert b1.max_hp == 125.0
    assert b1.hp == 125.0
    assert b1.base_speed == 125.0
    assert b1.base_damage == 12.5

    # Tick at 60 seconds (full decay)
    mode.tick(world, balls, 30.0)
    # total match time = 60, progress = 1.0
    # scale factor = 1.0 - 0.75 = 0.25
    # 200 * 0.25 = 50.0 (which is 50% of the original 100)
    assert b1.max_hp == 50.0
    assert b1.hp == 50.0
    assert b1.base_speed == 50.0
    assert b1.base_damage == 5.0

    # Test healing items
    import random
    random.seed(42) # Try to make it somewhat deterministic
    hp_pack = MockBooster("health_pack")
    hp_pack2 = MockBooster("hp_booster")
    speed_pack = MockBooster("speed_booster")
    world.boosters = [hp_pack, hp_pack2, speed_pack]

    mode.tick(world, balls, 1.0)
    assert speed_pack.active == True # Unaffected
    assert getattr(speed_pack, "_decay_checked", False) == False

    # hp_packs have 80% chance to be disabled
    # with seed 42, random.random() calls:
    # 1: 0.6394... (<0.8) -> disabled
    # 2: 0.0250... (<0.8) -> disabled
    assert hp_pack.active == False
    assert hp_pack2.active == False
    assert hp_pack._decay_checked == True
