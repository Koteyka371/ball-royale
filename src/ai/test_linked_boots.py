import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, team, x, y, vx, vy):
        self.team = team
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.is_alive = True
        self.speed_boost_timer = 0.0
        self.reflect_shield_timer = 0.0
        self.invulnerable_timer = 0.0
        self.ghost_timer = 0.0

class MockWorld:
    def __init__(self):
        self.arena = type("Arena", (), {"width": 800, "height": 600})()

def test_linked_boots_knockback_and_status():
    mode = GAME_MODES["linked_boots"]
    mode.active_timer = 10.0

    b1 = MockBall(team=1, x=100, y=100, vx=10, vy=10)
    b2 = MockBall(team=1, x=150, y=150, vx=0, vy=0)
    b3 = MockBall(team=2, x=200, y=200, vx=0, vy=0)

    world = MockWorld()
    balls = [b1, b2, b3]

    # Tick 1: Initialize previous velocity
    mode.tick(world, balls, 0.016)

    assert getattr(b1, "lb_prev_vx") == 10.0
    assert getattr(b1, "lb_prev_vy") == 10.0

    # Simulate sudden knockback on b1
    b1.vx = 200.0  # +190 speed change
    b1.vy = 200.0  # +190 speed change

    # Add status effect to b1
    b1.speed_boost_timer = 10.0
    b2.speed_boost_timer = 0.0

    # Tick 2: Should trigger knockback linking and status sharing
    mode.tick(world, balls, 0.016)

    assert b1.speed_boost_timer == 5.0
    assert b2.speed_boost_timer == 5.0

    assert b1.vx == 105.0
    assert b1.vy == 105.0
    assert b2.vx == 95.0
    assert b2.vy == 95.0
