import pytest
from unittest.mock import MagicMock
from ai.game_modes import TetheredRoyaleMode

class MockBall:
    def __init__(self, ball_id, ball_type="default"):
        self.id = ball_id
        self.ball_type = ball_type
        self.hp = 100.0
        self.stamina = 100.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 20.0
        self.damage = 20.0
        self.alive = True
        self.vx = 0.0
        self.vy = 0.0
        self.x = 0.0
        self.y = 0.0

def test_tethered_setup():
    mode = TetheredRoyaleMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager

    b1 = MockBall(1)
    b2 = MockBall(2)
    b3 = MockBall(3)
    b4 = MockBall(4, ball_type="spectator")

    balls = [b1, b2, b3, b4]

    mode.setup(world, balls)

    # Assert pairings
    alive_balls = [b1, b2, b3]
    paired_count = 0

    for b in alive_balls:
        target = getattr(b, "tether_target", None)
        if target:
            paired_count += 1
            assert target.tether_target == b # mutual link

    assert paired_count == 2

def test_tethered_tick_movement():
    mode = TetheredRoyaleMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager

    b1 = MockBall(1)
    b2 = MockBall(2)
    balls = [b1, b2]

    mode.setup(world, balls)

    # 1. Opposite movement
    b1.vx = -10.0
    b2.vx = 10.0
    mode.tick(world, balls, 0.1)

    # Should lose stamina
    assert b1.stamina < 100.0
    assert b2.stamina < 100.0

    # 2. Coordinated movement
    b1.vx = 10.0
    b2.vx = 10.0
    b1.stamina = 100.0
    b2.stamina = 100.0
    mode.tick(world, balls, 0.1)

    # Should gain speed and buff
    assert b1.stamina == 100.0
    assert b2.stamina == 100.0
    assert b1.speed > b1.base_speed
    assert b1.damage > b1.base_damage

def test_tethered_tick_elimination():
    mode = TetheredRoyaleMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager
    world.arena = MagicMock()
    world.arena.hazards = []

    b1 = MockBall(1)
    b2 = MockBall(2)
    balls = [b1, b2]

    mode.setup(world, balls)

    # First tick to register alive state
    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 0

    # Eliminate b1
    b1.alive = false = False

    # Tick again, should spawn hazard
    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "recoil_explosion"
    assert world.arena.hazards[0].damage == 50.0
