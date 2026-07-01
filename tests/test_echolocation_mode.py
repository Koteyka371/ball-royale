import pytest
from ai.game_modes import EcholocationMode

class MockArena:
    def __init__(self):
        self.is_night = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, type_name, data):
        self.events.append((type_name, data))

class MockBall:
    def __init__(self, id=0, ball_type="red"):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.perception_radius = 250.0

def test_echolocation_mode():
    mode = EcholocationMode()
    world = MockWorld()
    balls = [MockBall(1, "red"), MockBall(2, "blue")]

    mode.setup(world, balls)

    assert world.arena.is_night == True
    for b in balls:
        assert b.perception_radius == 60.0

    mode.tick(world, balls, delta=9.9)
    assert not mode.is_flashing

    # Tick past flash interval
    mode.tick(world, balls, delta=0.2)
    assert mode.is_flashing
    assert world.arena.is_night == False
    for b in balls:
        assert b.perception_radius == 1000.0

    # Tick past flash duration
    mode.tick(world, balls, delta=0.6)
    assert not mode.is_flashing
    assert world.arena.is_night == True
    for b in balls:
        assert b.perception_radius == 60.0
