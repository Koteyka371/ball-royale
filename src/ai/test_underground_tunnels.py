import pytest
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.underground = False
        self.is_invisible = False
        self.tunnel_cooldown = 0.0
        self.tunnel_target_x = 0.0
        self.tunnel_target_y = 0.0

def test_underground_tunnels_mode():
    mode = GAME_MODES.get("underground_tunnels")
    assert mode is not None

    world = MockWorld()
    b1 = MockBall(1, 100.0, 100.0)
    balls = [b1]

    mode.setup(world, balls)
    assert len(mode.tunnels) == 3
    assert len(world.arena.hazards) == 6

    # Manually place b1 near a tunnel
    t = mode.tunnels[0]
    b1.x = t.x1 + 10.0
    b1.y = t.y1 + 10.0

    # Tick should suck the ball in
    mode.tick(world, balls, delta=0.1)

    assert b1.underground is True
    assert b1.is_invisible is True
    assert b1.tunnel_target_x == t.x2
    assert b1.tunnel_target_y == t.y2

    # Travel underground
    mode.tick(world, balls, delta=0.5)

    # Should move toward t.x2, t.y2
    dist_after = math.sqrt((b1.x - t.x2)**2 + (b1.y - t.y2)**2)
    dist_initial = math.sqrt((t.x1 - t.x2)**2 + (t.y1 - t.y2)**2)
    assert dist_after < dist_initial

    # Manually put it near exit
    b1.x = t.x2 - 1.0
    b1.y = t.y2 - 1.0
    mode.tick(world, balls, delta=0.1)

    # Should emerge
    assert b1.underground is False
    assert b1.is_invisible is False
    assert b1.tunnel_cooldown > 0.0

def test_underground_tunnels_cooldown():
    mode = GAME_MODES.get("underground_tunnels")
    world = MockWorld()
    b1 = MockBall(1, 100.0, 100.0)
    balls = [b1]

    mode.setup(world, balls)
    t = mode.tunnels[0]

    b1.x = t.x1 + 5.0
    b1.y = t.y1 + 5.0
    b1.tunnel_cooldown = 0.5

    mode.tick(world, balls, delta=0.1)

    # Should not get sucked in because of cooldown
    assert b1.underground is False
    assert b1.tunnel_cooldown == pytest.approx(0.4)
