from unittest.mock import MagicMock
from ai.game_modes import PeriodicInvertControlsMutatorMode

class MockBall:
    def __init__(self, name="TestBall"):
        self.name = name
        self.alive = True
        self.ball_type = "player"
        self.invert_timer = 0.0

def test_periodic_invert_controls_mutator():
    mode = PeriodicInvertControlsMutatorMode()
    world = MagicMock()
    del world.arena # prevent nested property errors

    # ensure default state
    world.periodic_invert_timer = 0.0
    world.periodic_invert_active = False

    balls = [MockBall("B1"), MockBall("B2")]

    # Tick for interval duration (10 seconds)
    # Timer starts at 0, not active.
    # At 10 seconds, it should become active.
    mode.tick(world, balls, delta=9.9)
    assert world.periodic_invert_active == False
    for b in balls:
        assert b.invert_timer == 0.0

    mode.tick(world, balls, delta=0.2)
    assert world.periodic_invert_active == True
    assert world.periodic_invert_timer == 0.0

    # Now it is active, next tick should apply invert_timer
    mode.tick(world, balls, delta=0.5)
    assert world.periodic_invert_active == True
    for b in balls:
        assert b.invert_timer >= 0.1

    # Tick for duration (5 seconds)
    mode.tick(world, balls, delta=5.0)
    assert world.periodic_invert_active == False
    assert world.periodic_invert_timer == 0.0
