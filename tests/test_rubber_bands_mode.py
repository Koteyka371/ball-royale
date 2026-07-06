import pytest
from unittest.mock import MagicMock
from src.ai.game_modes import RubberBandsMode

class MockBall:
    def __init__(self, id, team, x, y):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "default"
        self.radius = 10.0
        self.hp = 100.0
        self.damage = 10.0
        self.vx = 0.0
        self.vy = 0.0

def test_rubber_bands_setup():
    mode = RubberBandsMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager

    b1 = MockBall(1, 1, 0, 0)
    b2 = MockBall(2, 1, 10, 10)
    b3 = MockBall(3, 2, 20, 20)

    balls = [b1, b2, b3]
    mode.setup(world, balls)

    # Team 1 should be linked to each other
    assert hasattr(b1, "rubber_band_target")
    assert hasattr(b2, "rubber_band_target")
    assert b1.rubber_band_target == b2
    assert b2.rubber_band_target == b1

    # Team 2 only has 1 ball, should not have a target (or target is None)
    assert not hasattr(b3, "rubber_band_target") or b3.rubber_band_target is None

    assert b1.rubber_band_immune_timer == 0.0
    assert not b1.is_snapping_rubber_band

def test_rubber_bands_tick_snap():
    mode = RubberBandsMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager

    b1 = MockBall(1, 1, 0, 0)
    # Distance > 250
    b2 = MockBall(2, 1, 300, 0)

    balls = [b1, b2]
    mode.setup(world, balls)

    mode.tick(world, balls, 0.1)

    assert b1.is_snapping_rubber_band
    assert b2.is_snapping_rubber_band

    # b1 pulls towards b2
    assert b1.vx > 0
    # b2 pulls towards b1
    assert b2.vx < 0

def test_rubber_bands_damage():
    mode = RubberBandsMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager

    b1 = MockBall(1, 1, 0, 0)
    b2 = MockBall(2, 1, 300, 0)
    # Enemy right in between
    b3 = MockBall(3, 2, 0, 0)

    balls = [b1, b2, b3]
    mode.setup(world, balls)

    b3.x = 5.0 # Close to b1
    if hasattr(world, '_deal_damage'):
        del world._deal_damage

    mode.tick(world, balls, 0.1)

    # b1 is snapping and should hit b3
    assert b3.hp < 100.0
    assert b3.rubber_band_immune_timer == 0.5

    # Next tick, should be immune
    hp_after_hit = b3.hp
    mode.tick(world, balls, 0.1)
    assert b3.hp == hp_after_hit
