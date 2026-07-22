import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id=0, x=500.0, y=500.0):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100.0
        self.is_stunned = False
        self.stun_timer = 0.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

def test_collapsing_ceiling_setup():
    mode = GAME_MODES["collapsing_ceiling"]
    world = MockWorld()
    balls = [MockBall(i) for i in range(2)]

    mode.setup(world, balls)

    assert len(mode.zones) == 3
    assert mode.collapse_timer == mode.max_collapse_timer

    for zone in mode.zones:
        assert zone["height"] == world.arena.height

def test_collapsing_ceiling_tick_shrinks():
    mode = GAME_MODES["collapsing_ceiling"]
    world = MockWorld()
    balls = [MockBall(i) for i in range(2)]

    mode.setup(world, balls)
    initial_height = mode.zone_height

    # Tick updates height
    mode.tick(world, balls, delta=1.0)

    assert mode.zone_height < initial_height
    assert mode.zone_height == initial_height - 50.0

def test_collapsing_ceiling_damage_and_stun():
    mode = GAME_MODES["collapsing_ceiling"]
    world = MockWorld()
    ball_in = MockBall(0, x=500.0, y=500.0)
    ball_out = MockBall(1, x=100.0, y=100.0)
    balls = [ball_in, ball_out]

    mode.setup(world, balls)

    # Force zone to center
    mode.zones = [{"x": 500.0, "y": 500.0, "width": 200.0, "height": 800.0}]

    # Fast forward to collapse
    mode.collapse_timer = 0.01
    mode.tick(world, balls, delta=0.02)

    # Ball in should be safe
    assert ball_in.alive is True
    assert ball_in.hp == 100.0
    assert ball_in.is_stunned is False

    # Ball out should take massive damage and be stunned
    assert ball_out.alive is False
    assert ball_out.hp == 0.0
    assert ball_out.is_stunned is True
    assert ball_out.stun_timer == 2.0
