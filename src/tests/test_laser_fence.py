import pytest
from ai.laser_fence import LaserFenceMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x=0.0, y=0.0, hp=100.0, alive=True, ball_type="player"):
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = alive
        self.ball_type = ball_type

def test_setup():
    mode = LaserFenceMode()
    world = MockWorld()
    balls = []

    mode.fences = [{"dummy": 1}]
    mode.spawn_timer = 10.0

    mode.setup(world, balls)

    assert mode.fences == []
    assert mode.spawn_timer == 0.0

def test_tick_spawns_fence():
    mode = LaserFenceMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)

    # Tick below spawn_interval
    mode.tick(world, balls, delta=4.0)
    assert len(mode.fences) == 0

    # Tick above spawn_interval
    mode.tick(world, balls, delta=1.0)
    assert len(mode.fences) == 1

    fence = mode.fences[0]
    assert fence["orientation"] in ["horizontal", "vertical"]
    assert fence["dir"] in [-1, 1]

def test_tick_moves_fence():
    mode = LaserFenceMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)

    mode.fences = [{
        "orientation": "horizontal",
        "pos": 0.0,
        "dir": 1
    }]

    mode.tick(world, balls, delta=1.0)

    assert len(mode.fences) == 1
    # 0 + 100 * 1.0 * 1 = 100
    assert abs(mode.fences[0]["pos"] - 100.0) < 0.001

def test_tick_damages_ball():
    mode = LaserFenceMode()
    world = MockWorld()

    ball = MockBall(x=500.0, y=200.0, hp=100.0)
    balls = [ball]

    mode.setup(world, balls)

    mode.fences = [{
        "orientation": "horizontal",
        "pos": 100.0,
        "dir": 1
    }]

    # Tick by 1.0 -> 100 damage
    mode.tick(world, balls, delta=1.0)

    assert ball.hp == 0.0
    assert ball.alive == False

    # Verify fence moved
    assert abs(mode.fences[0]["pos"] - 200.0) < 0.001

def test_cleanup_offscreen_fences():
    mode = LaserFenceMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)

    mode.fences = [
        {
            "orientation": "horizontal",
            "pos": 1000.0,
            "dir": 1
        },
        {
            "orientation": "vertical",
            "pos": 0.0,
            "dir": -1
        }
    ]

    mode.tick(world, balls, delta=1.1)

    # horizontal: 1000 + 100 * 1.1 * 1 = 1110 (offscreen since height=1000 and +100 threshold = 1100)
    # vertical: 0 + 100 * 1.1 * -1 = -110 (offscreen since -100 threshold)
    assert len(mode.fences) == 0
