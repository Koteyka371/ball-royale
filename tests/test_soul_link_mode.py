import pytest
from unittest.mock import MagicMock
from ai.game_modes import SoulLinkMode

class MockBall:
    def __init__(self, ball_id, ball_type="tank"):
        self.id = ball_id
        self.ball_type = ball_type
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.stun_timer = 0.0
        self.burn_timer = 0.0
        self.poison_timer = 0.0

def test_soul_link_setup():
    mode = SoulLinkMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager


    b1 = MockBall(1)
    b2 = MockBall(2)
    b3 = MockBall(3)
    b4 = MockBall(4, ball_type="spectator")

    balls = [b1, b2, b3, b4]

    mode.setup(world, balls)

    alive_balls = [b1, b2, b3]
    paired_count = 0
    unpaired_count = 0

    for b in alive_balls:
        if getattr(b, "soul_link_target", None):
            paired_count += 1
            assert b.soul_link_target.soul_link_target == b # mutual link
        else:
            unpaired_count += 1

    assert paired_count == 2
    assert unpaired_count == 1

def test_soul_link_tick_hp_sharing():
    mode = SoulLinkMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager


    b1 = MockBall(1)
    b2 = MockBall(2)
    balls = [b1, b2]

    mode.setup(world, balls)

    assert b1.soul_link_target == b2
    assert b2.soul_link_target == b1

    # Tick 1: normal, no damage
    mode.tick(world, balls, 0.1)

    # b1 takes 20 damage
    b1.hp = 80.0

    # Tick 2: b1 damage should flow to b2
    mode.tick(world, balls, 0.1)

    assert b2.hp == 80.0

    # Tick 3: b2 took damage internally in tick 2, ensure it doesn't bounce back
    mode.tick(world, balls, 0.1)
    assert b1.hp == 80.0
    assert b2.hp == 80.0

def test_soul_link_tick_status_sharing():
    mode = SoulLinkMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager


    b1 = MockBall(1)
    b2 = MockBall(2)
    balls = [b1, b2]

    mode.setup(world, balls)

    # b1 gets stunned for 2.0s
    b1.stun_timer = 2.0

    mode.tick(world, balls, 0.1)

    assert b2.stun_timer == 2.0

    # Check no reflection back
    mode.tick(world, balls, 0.1)
    assert b1.stun_timer == 2.0
