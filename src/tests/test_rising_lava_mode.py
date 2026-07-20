import pytest
import sys
sys.path.append('src')
from ai.game_modes import RisingLavaMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, id, ball_type):
        self.id = id
        self.ball_type = ball_type
        self.team = ball_type
        self.x = 500.0
        self.y = 500.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True

def test_rising_lava_mode_setup():
    mode = RisingLavaMode()
    world = MockWorld()
    balls = [MockBall(1, "warrior")]

    mode.setup(world, balls)

    assert mode.lava_y == 1000.0
    assert len(mode.platforms) == 15
    for p in mode.platforms:
        assert 100.0 <= p["x"] <= 900.0
        assert 100.0 <= p["y"] <= 900.0

def test_rising_lava_mode_tick():
    mode = RisingLavaMode()
    world = MockWorld()

    b1 = MockBall(1, "warrior")
    b1.x = 500.0
    b1.y = 800.0 # Will be submerged first

    b2 = MockBall(2, "scout")
    b2.x = 500.0
    b2.y = 200.0 # Will survive longer

    balls = [b1, b2]

    mode.setup(world, balls)

    # Force platform clear so they don't accidentally stand on one
    mode.platforms = []

    assert mode.lava_y == 1000.0

    # Tick for some time to make lava rise
    for _ in range(300):
        mode.tick(world, balls, delta=0.1)

    # rise_rate is 15.0, so after 30 ticks (300 * 0.1), it should rise by 450
    # lava_y should be 1000.0 - 450.0 = 550.0

    assert mode.lava_y == pytest.approx(550.0)

    # b1 (y=800) is > lava_y (550), so it should take damage
    assert b1.hp < 100.0

    # b2 (y=200) is < lava_y (550), so it should not take damage
    assert b2.hp == 100.0

def test_rising_lava_platforms_destroyed():
    mode = RisingLavaMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)

    # Add manual platforms
    mode.platforms = [
        {"x": 500, "y": 800, "radius": 50}, # Low
        {"x": 500, "y": 200, "radius": 50}  # High
    ]

    # Fast forward lava to y = 500
    for _ in range(500):
        mode.tick(world, balls, delta=0.1) # 500 * 15 * 0.1 = 750 rising => lava_y = 250

    assert mode.lava_y == pytest.approx(250.0)

    # Low platform (y=800) > lava_y (250) should be destroyed
    # High platform (y=200) < lava_y (250) should remain
    assert len(mode.platforms) == 1
    assert mode.platforms[0]["y"] == 200
