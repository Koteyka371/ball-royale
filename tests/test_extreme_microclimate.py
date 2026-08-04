import pytest
from src.ai.game_modes import ExtremeMicroclimateMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.mutators_active = False

class MockBall:
    def __init__(self, x, y):
        self.id = id(self)
        self.x = x
        self.y = y
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.speed = 100.0
        self.speed_boost_timer = 0.0
        self.speed_boost_multiplier = 1.0
        self.speed_debuff_timer = 0.0
        self.speed_debuff_multiplier = 1.0
        self.damage = 10.0
        self.hologram_clones = []

def test_extreme_microclimate_setup_and_flip():
    mode = ExtremeMicroclimateMode()
    world = MockWorld()
    b1 = MockBall(500, 500)
    balls = [b1]

    mode.setup(world, balls)

    # Force one sector to be at the ball's exact location to guarantee effects
    mode.sectors[0] = {
        "x": 500,
        "y": 500,
        "radius": 150.0,
        "weather": "heatwave"
    }

    # Tick with delta < flip_interval to apply heatwave
    mode.tick(world, balls, delta=0.5)

    assert b1.speed_boost_timer > 0, "Heatwave should apply speed boost"
    assert b1.speed_boost_multiplier == 1.3, "Heatwave speed multiplier should be 1.3"
    assert b1.hp < 100.0, "Heatwave should deal small damage"

    old_hp = b1.hp

    # Jump time to flip interval
    mode.tick(world, balls, delta=5.0)

    # Weather should now be blizzard
    assert mode.sectors[0]["weather"] == "blizzard", "Weather should have flipped to blizzard"

    # Tick again to apply blizzard
    mode.tick(world, balls, delta=0.5)

    assert b1.speed_debuff_timer > 0, "Blizzard should apply speed debuff"
    assert b1.speed_debuff_multiplier == 0.6, "Blizzard speed debuff multiplier should be 0.6"
    assert b1.hp < old_hp, "Blizzard should deal damage"

def test_extreme_microclimate_kill():
    mode = ExtremeMicroclimateMode()
    world = MockWorld()
    b1 = MockBall(500, 500)
    b1.hp = 1.0  # low hp to test death
    balls = [b1]

    mode.setup(world, balls)
    mode.sectors[0] = {
        "x": 500,
        "y": 500,
        "radius": 150.0,
        "weather": "heatwave"
    }

    # Tick to apply damage
    mode.tick(world, balls, delta=1.0)

    assert b1.alive == False, "Ball should be killed by heatwave damage"
