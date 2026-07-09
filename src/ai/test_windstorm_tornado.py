import sys
import os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

def test_windstorm_tornado_spawn():
    mode = GAME_MODES["windstorm"]
    world = MockWorld()

    # Fast forward to trigger tornado spawn
    mode.tornado_timer = 0.0
    mode.tick(world, [], 0.1)

    assert len(world.arena.hazards) == 1
    tornado = world.arena.hazards[0]

    assert getattr(tornado, "kind", "") == "tornado"
    assert getattr(tornado, "duration", 0.0) > 0.0
    assert hasattr(tornado, "vx")
    assert hasattr(tornado, "vy")

if __name__ == '__main__':
    test_windstorm_tornado_spawn()
    print("Tests passed.")
