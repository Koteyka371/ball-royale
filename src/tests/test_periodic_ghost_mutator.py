import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, alive=True, ball_type="player"):
        self.id = id
        self.alive = alive
        self.ball_type = ball_type
        self.intangible = False
        self.intangible_timer = 0.0
        self.ghost_mode_active = False
        self.ghost_mode_timer = 0.0

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

def test_periodic_ghost_mutator():
    mode = GAME_MODES['periodic_ghost_mutator']
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2, alive=False)
    b3 = MockBall(3, ball_type="spectator")
    balls = [b1, b2, b3]

    mode.setup(world, balls)

    assert b1.intangible == False

    # Tick past duration (duration is 10.0)
    mode.tick(world, balls, delta=10.1)

    # Check if event was fired
    assert any(e[0] == "ghost_mode" for e in world.events)

    # Check if valid ball got traits
    assert b1.intangible == True
    assert b1.intangible_timer == 3.0
    assert b1.ghost_mode_active == True
    assert b1.ghost_mode_timer == 3.0

    # Dead balls and spectators should not get traits
    assert b2.intangible == False
    assert b3.intangible == False
