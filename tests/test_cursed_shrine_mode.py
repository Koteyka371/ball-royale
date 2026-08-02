import pytest
from src.ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.bounds = {'x_min': 0, 'x_max': 800, 'y_min': 0, 'y_max': 600}
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, bid, x, y):
        self.id = bid
        self.x = x
        self.y = y
        self.radius = 10.0
        self.alive = True
        self.ball_type = "normal"
        self.speed = 100.0
        self.base_speed = 100.0
        self.damage_multiplier = 1.0
        self.max_hp = 100.0
        self.base_max_hp = 100.0
        self.hp = 100.0

def test_cursed_shrine_mode():
    mode = GAME_MODES["cursed_shrine"]
    world = MockWorld()

    mode.setup(world)

    assert len(mode.shrines) >= 2
    assert len(world.arena.hazards) >= 2

    shrine = mode.shrines[0]
    shrine.x = 400
    shrine.y = 300
    shrine.radius = 40

    ball1 = MockBall(1, 400, 300) # Inside shrine
    ball2 = MockBall(2, 100, 100) # Outside shrine

    mode.tick(world, [ball1, ball2], 1.0)

    # Ball 1 interacted
    assert ball1.id in shrine.used_by
    assert ball1.speed == pytest.approx(120.0)
    assert ball1.base_speed == pytest.approx(120.0)
    assert ball1.damage_multiplier == pytest.approx(1.2)
    assert ball1.max_hp == pytest.approx(50.0)
    assert ball1.base_max_hp == pytest.approx(50.0)
    assert ball1.hp == pytest.approx(50.0)

    # Ball 2 did not interact
    assert ball2.id not in shrine.used_by
    assert ball2.speed == pytest.approx(100.0)
    assert ball2.max_hp == pytest.approx(100.0)

    # Tick again, Ball 1 shouldn't be affected again
    mode.tick(world, [ball1, ball2], 1.0)
    assert ball1.speed == pytest.approx(120.0)
    assert ball1.max_hp == pytest.approx(50.0)
