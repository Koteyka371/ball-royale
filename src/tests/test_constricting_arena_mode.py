import pytest
from system.test_crowd_system import MockBall
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_constricting_arena_mode_shrinks_and_damages():
    mode = GAME_MODES.get("constricting_arena")
    assert mode is not None

    world = MockWorld()
    b1 = MockBall(1, "team1", "player")
    b1.x = 500
    b1.y = 500
    b1.hp = 100
    b1.alive = True
    b1.radius = 15
    b1.slow_timer = 0

    b2 = MockBall(2, "team2", "player")
    b2.x = 10
    b2.y = 500
    b2.hp = 100
    b2.alive = True
    b2.radius = 15
    b2.slow_timer = 0

    balls = [b1, b2]

    # Tick 1 second
    mode.tick(world, balls, 1.0)

    # Arena shrinks by 10 (shrink_speed)
    assert world.arena.width == 990.0
    assert world.arena.height == 990.0

    # b1 is in the center, shouldn't be affected
    assert b1.x == 500
    assert b1.hp == 100
    assert b1.slow_timer == 0

    # b2 is out of bounds (x < radius), should be pushed to radius (15) and take damage
    assert b2.x == 15
    assert b2.hp == 80.0
    assert b2.slow_timer == 1.0
