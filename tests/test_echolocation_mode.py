import pytest
from ai.game_modes import EcholocationMode

class MockArena:
    def __init__(self):
        self.is_night = False
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []
        self.boosters = []

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
        assert b.pulse_interval == 3.0
        assert b.pulse_duration == 0.5
        assert b.pulse_timer == 0.0
        assert b.is_pulsing == False

    # Tick past pulse interval
    mode.tick(world, balls, delta=3.0)
    assert world.arena.is_night == True
    for b in balls:
        assert b.is_pulsing == True
        assert b.perception_radius == 1000.0

    # Tick past pulse duration
    mode.tick(world, balls, delta=0.6)
    assert world.arena.is_night == True
    for b in balls:
        assert b.is_pulsing == False
        assert b.perception_radius == 60.0
