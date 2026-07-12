import pytest
from unittest.mock import MagicMock
from src.ai.game_modes import GameMode, ScorchingSunMode

class MockBall:
    def __init__(self, x=0, y=0, hp=100.0, stamina=100.0):
        self.x = x
        self.y = y
        self.hp = hp
        self.stamina = stamina
        self.alive = True
        self.ball_type = "test_ball"
        self.radius = 15.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.is_night = False
        self.weather = "normal"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type_name, data):
        self.events.append((type_name, data))

def test_scorching_sun_mode_safe_zone():
    mode = ScorchingSunMode()
    world = MockWorld()

    # One ball inside the safe zone (center), one outside
    ball_safe = MockBall(x=500.0, y=500.0)
    ball_unsafe = MockBall(x=10.0, y=10.0)

    balls = [ball_safe, ball_unsafe]

    mode.setup(world, balls)
    assert mode.safe_zone_radius == 500.0

    # Tick with a large delta to see effects clearly
    mode.tick(world, balls, delta=1.0)

    # Safe zone should shrink
    assert mode.safe_zone_radius < 500.0

    # Safe ball should have full hp and stamina
    assert ball_safe.hp == 100.0
    assert ball_safe.stamina == 100.0

    # Unsafe ball should take damage and lose stamina
    assert ball_unsafe.hp < 100.0
    assert ball_unsafe.stamina < 100.0

def test_scorching_sun_mode_heat_increase():
    mode = ScorchingSunMode()
    world = MockWorld()
    ball_unsafe = MockBall(x=10.0, y=10.0)
    balls = [ball_unsafe]

    mode.setup(world, balls)

    # First tick damage
    initial_hp = ball_unsafe.hp
    mode.tick(world, balls, delta=1.0)
    damage_tick_1 = initial_hp - ball_unsafe.hp

    # Fast forward time
    mode.timer = 60.0

    hp_before = ball_unsafe.hp
    mode.tick(world, balls, delta=1.0)
    damage_tick_60 = hp_before - ball_unsafe.hp

    # Damage should increase over time
    assert damage_tick_60 > damage_tick_1

def test_scorching_sun_death():
    mode = ScorchingSunMode()
    world = MockWorld()
    ball_unsafe = MockBall(x=10.0, y=10.0, hp=5.0)
    balls = [ball_unsafe]

    mode.setup(world, balls)
    mode.tick(world, balls, delta=1.0)

    assert not ball_unsafe.alive
    assert ball_unsafe.hp <= 0
