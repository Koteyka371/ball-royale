import pytest
from unittest.mock import MagicMock
from ai.game_modes import EntangledSwapHazardMode

class MockBall:
    def __init__(self, bid, x, y, hp=100.0):
        self.id = bid
        self.x = x
        self.y = y
        self.vx = 10.0
        self.vy = 10.0
        self.hp = hp
        self.alive = True
        self.ball_type = "player"

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

def test_entangled_swap_hazard_setup():
    mode = EntangledSwapHazardMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager

    balls = [MockBall(1, 10, 10), MockBall(2, 20, 20), MockBall(3, 30, 30)]
    mode.setup(world, balls)

    # Entangled pairs
    has_partner = 0
    no_partner = 0
    for b in balls:
        if getattr(b, "random_entangled_with", None) is not None:
            has_partner += 1
            partner = b.random_entangled_with
            assert partner.random_entangled_with == b
        else:
            no_partner += 1

    assert has_partner == 2
    assert no_partner == 1
    assert len(mode.prev_state) == 3

def test_entangled_swap_hazard_tick_massive_damage():
    mode = EntangledSwapHazardMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager

    world.events = []
    balls = [MockBall(1, 100, 100), MockBall(2, 500, 500)]
    mode.setup(world, balls)

    b1, b2 = balls[0], balls[1]

    # Verify initial state
    assert getattr(b1, "random_entangled_with", None) == b2
    assert getattr(b2, "random_entangled_with", None) == b1

    # Change velocities for tracking
    b1.vx, b1.vy = 15.0, 15.0
    b2.vx, b2.vy = -5.0, -5.0

    # Apply massive damage (>30 threshold)
    b1.hp -= 35.0

    mode.tick(world, balls, 0.016)

    # Positions should be swapped
    assert b1.x == 500
    assert b1.y == 500
    assert b2.x == 100
    assert b2.y == 100

    # Velocities should be swapped
    assert b1.vx == -5.0
    assert b1.vy == -5.0
    assert b2.vx == 15.0
    assert b2.vy == 15.0

    # Event should be added
    assert len(world.events) == 1
    assert world.events[0][0] == "position_swapped"
    assert world.events[0][1]["ball_a"] == 1
    assert world.events[0][1]["ball_b"] == 2

def test_entangled_swap_hazard_tick_minor_damage():
    mode = EntangledSwapHazardMode()
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager

    world.events = []
    balls = [MockBall(1, 100, 100), MockBall(2, 500, 500)]
    mode.setup(world, balls)

    b1, b2 = balls[0], balls[1]

    # Change velocities for tracking
    b1.vx, b1.vy = 15.0, 15.0
    b2.vx, b2.vy = -5.0, -5.0

    # Apply minor damage (<30 threshold)
    b1.hp -= 15.0

    mode.tick(world, balls, 0.016)

    # Positions should NOT be swapped
    assert b1.x == 100
    assert b1.y == 100
    assert b2.x == 500
    assert b2.y == 500

    # Velocities should NOT be swapped
    assert b1.vx == 15.0
    assert b1.vy == 15.0
    assert b2.vx == -5.0
    assert b2.vy == -5.0

    # No event should be added
    assert len(world.events) == 0
