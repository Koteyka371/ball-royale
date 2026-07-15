import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_time_loop_field():
    mode = GAME_MODES.get("time_loop_field")
    assert mode is not None

    world = MockWorld()
    balls = [MockBall(1, 100, 100), MockBall(2, 500, 500)]

    mode.setup(world, balls)

    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "time_loop_field"

    # tick 1, ball 2 is in field, ball 1 is not
    mode.tick(world, balls, 0.0)

    assert 1 not in mode.recorded_states
    assert 2 in mode.recorded_states

    # modify ball 2
    balls[1].x = 600
    balls[1].y = 600
    balls[1].hp = 50

    # tick 2, advance time by 3 seconds
    mode.tick(world, balls, 3.0)

    # ball 2 should be reset to 500, 500, 100 hp
    assert balls[1].x == 500
    assert balls[1].y == 500
    assert balls[1].hp == 100
