import pytest
from ai.game_modes import GAME_MODES

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

def test_shrinking_danger_zone_mode():
    mode = GAME_MODES["shrinking_danger_zone"]
    world = MockWorld()
    balls = [MockBall(i) for i in range(2)]
    mode.setup(world, balls)

    assert mode.zone_radius == 500.0

    mode.tick(world, balls, delta=1.0)
    assert mode.zone_radius < 500.0

    balls[0].x = 1000.0
    balls[0].y = 1000.0
    initial_hp = balls[0].hp
    mode.tick(world, balls, delta=1.0)
    assert balls[0].hp < initial_hp

    balls[0].hp = 1.0
    mode.tick(world, balls, delta=1.0)
    assert not balls[0].alive
    assert balls[0].killer == "Danger Zone"
