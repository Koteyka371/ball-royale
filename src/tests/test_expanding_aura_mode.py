import pytest
from ai.game_modes import GAME_MODES, ExpandingAuraEventMode

class MockBall:
    def __init__(self, id=1, hp=100.0, alive=True):
        self.id = id
        self.hp = hp
        self.alive = alive
        self.damage_multiplier = 1.0
        self.weather_immunity_timer = 0.0

def test_expanding_aura_event_mode():
    mode = GAME_MODES["expanding_aura_event"]
    assert isinstance(mode, ExpandingAuraEventMode)

    world = type("MockWorld", (), {})()
    ball1 = MockBall(id=1, hp=100.0)
    balls = [ball1]

    mode.setup(world, balls)

    # Tick 1: initializes stats
    mode.tick(world, balls, delta=1.0)

    # Scale should expand
    expected_scale = 1.0 + 0.5 * 1.0
    assert getattr(ball1, "cosmetic_aura_scale") == expected_scale
    assert ball1.damage_multiplier == 1.0 * expected_scale

    # Tick 2: expands further
    mode.tick(world, balls, delta=1.0)
    expected_scale += 0.5
    assert getattr(ball1, "cosmetic_aura_scale") == expected_scale
    assert ball1.damage_multiplier == 1.0 * expected_scale

    # Take damage, should reset on next tick
    ball1.hp = 80.0
    mode.tick(world, balls, delta=1.0)
    # Aura scale resets to 1.0, then expands by delta (0.5)
    expected_scale = 1.0 + 0.5 * 1.0
    assert getattr(ball1, "cosmetic_aura_scale") == expected_scale
    assert ball1.damage_multiplier == 1.0 * expected_scale

    # Test max scale
    mode.tick(world, balls, delta=10.0)
    assert getattr(ball1, "cosmetic_aura_scale") == 3.0
    assert ball1.damage_multiplier == 3.0
