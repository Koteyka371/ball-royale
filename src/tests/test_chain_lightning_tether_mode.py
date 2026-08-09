import pytest
from ai.game_modes import GAME_MODES, ChainLightningTetherMode
from unittest.mock import MagicMock

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.ball_type = "player"
        self.alive = True
        self.stun_timer = 0.0

def test_chain_lightning_tether_setup():
    mode = ChainLightningTetherMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager
    balls = [MockBall(1, 0, 0), MockBall(2, 100, 100)]

    mode.setup(world, balls)

    assert len(mode.link_durations) == 2
    assert mode.link_durations[1]["target_id"] is None
    assert mode.link_durations[1]["duration"] == 0.0

def test_chain_lightning_tether_tick_link_and_damage():
    mode = ChainLightningTetherMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager
    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 50, 0) # Close enough to link
    balls = [b1, b2]

    mode.setup(world, balls)

    # Tick 1: establish link
    mode.tick(world, balls, 1.0)

    assert mode.link_durations[1]["target_id"] == 2
    assert mode.link_durations[1]["duration"] == 0.0

    # Tick 2: ramp damage
    mode.tick(world, balls, 1.0)

    assert mode.link_durations[1]["duration"] == 1.0

    current_damage = mode.damage_base + mode.damage_ramp_rate * 1.0
    assert b1.hp == max(0.0, 100.0 - current_damage * 1.0)
    assert b1.chain_lightning_target == 2

def test_chain_lightning_tether_tick_break_link_stun():
    mode = ChainLightningTetherMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager
    world.add_event = MagicMock()

    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 50, 0)
    balls = [b1, b2]

    mode.setup(world, balls)

    # Tick 1: establish link
    mode.tick(world, balls, 1.0)
    assert mode.link_durations[1]["target_id"] == 2

    # Move too far
    b2.x = 400.0

    # Tick 2: break link, stun
    mode.tick(world, balls, 1.0)

    assert mode.link_durations[1]["target_id"] is None
    assert b1.stun_timer == 1.0
    world.add_event.assert_any_call("tether_broken", {"id": 1, "message": "Link broken! Stunned!"})
