import pytest
from ai.game_modes import GAME_MODES
from tests.simulate_battle import BattleSimulation

class MockArena:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id_val, btype="warrior"):
        self.id = id_val
        self.ball_type = btype
        self.alive = True
        self.x = 500.0
        self.y = 500.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.team = btype

    @property
    def position(self):
        return self

def test_moving_safe_zone_setup():
    mode = GAME_MODES["moving_safe_zone"]
    world = MockWorld()
    balls = [MockBall(i) for i in range(10)]

    mode.setup(world, balls)

    assert mode.zone_x == 500.0
    assert mode.zone_y == 500.0
    assert mode.zone_target_x == 500.0
    assert mode.zone_target_y == 500.0
    assert mode.zone_radius == 500.0

def test_moving_safe_zone_tick():
    mode = GAME_MODES["moving_safe_zone"]
    world = MockWorld()
    balls = [MockBall(1)]
    mode.setup(world, balls)

    # Force zone target away
    mode.zone_target_x = 0.0
    mode.zone_target_y = 0.0

    mode.tick(world, balls, delta=1.0)

    # Should move towards target
    assert mode.zone_x < 500.0
    assert mode.zone_y < 500.0

    # Should shrink
    assert mode.zone_radius < 500.0

    # Place ball far outside zone
    balls[0].x = 1000.0
    balls[0].y = 1000.0

    initial_hp = balls[0].hp
    mode.tick(world, balls, delta=1.0)

    # Should take damage
    assert balls[0].hp < initial_hp

    # Deal enough damage to kill
    balls[0].hp = 5.0
    mode.tick(world, balls, delta=1.0)

    assert not balls[0].alive
    assert balls[0].killer == "Danger Zone"
