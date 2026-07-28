import pytest
from ai.game_modes import GAME_MODES, BlackHoleNetworkMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, x=500.0, y=500.0):
        self.id = id(self)
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.ball_type = "player"

def test_black_hole_network_spawn():
    mode = BlackHoleNetworkMode()
    world = MockWorld()
    balls = [MockBall()]

    mode.spawn_interval = 2.0
    mode.spawn_timer = 1.99
    mode.tick(world, balls, delta=0.02)

    assert len(mode.black_holes) >= 3
    assert len(mode.black_holes) <= 5

    # Check if links are correct
    for i, bh in enumerate(mode.black_holes):
        assert "link" in bh
        assert bh["link"] == mode.black_holes[(i + 1) % len(mode.black_holes)]

    assert any(e[0] == "black_hole_network_spawn" for e in world.events)

def test_black_hole_network_pull_and_transport():
    mode = BlackHoleNetworkMode()
    world = MockWorld()

    # Create two black holes manually
    bh1 = {"x": 500.0, "y": 500.0, "radius": 40.0, "lifetime": 10.0, "cooldown": 0.0}
    bh2 = {"x": 800.0, "y": 800.0, "radius": 40.0, "lifetime": 10.0, "cooldown": 0.0}
    bh1["link"] = bh2
    bh2["link"] = bh1
    mode.black_holes = [bh1, bh2]

    # Test pull
    b_pull = MockBall(x=550.0, y=500.0) # Within pull range (160)
    mode.tick(world, [b_pull], delta=1.0) # 1 second to apply full pull strength
    assert b_pull.vx < 0 # Pulled towards 500

    # Test transport
    b_transport = MockBall(x=510.0, y=500.0) # Within radius (40)
    mode.tick(world, [b_transport], delta=0.02)
    assert b_transport.x == 800.0
    assert b_transport.y == 800.0
    assert bh1["cooldown"] > 0.0
    assert bh2["cooldown"] > 0.0
