import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, x, y):
        self.id = 1
        self.ball_type = "warrior"
        self.alive = True
        self.x = x
        self.y = y
        self.hp = 100.0

def test_supercell_storm_spawn():
    mode = GAME_MODES["supercell_storm"]
    world = MockWorld()
    mode.setup(world, [])

    mode.wind_timer = 0.0
    mode.tick(world, [], 0.1)

    assert len(world.arena.hazards) == 1
    tornado = world.arena.hazards[0]

    assert getattr(tornado, "kind", "") == "supercell_tornado"
    assert getattr(tornado, "duration", 0.0) > 0.0
    assert hasattr(tornado, "vx")
    assert hasattr(tornado, "vy")

def test_supercell_storm_lightning():
    mode = GAME_MODES["supercell_storm"]
    world = MockWorld()
    mode.setup(world, [])

    # Spawn tornado
    mode.wind_timer = 0.0
    mode.tick(world, [], 0.1)

    tornado = world.arena.hazards[0]
    tornado.x = 500
    tornado.y = 500
    tornado.radius = 100.0

    # Ball inside outer vortex (inner radius 30, outer 100)
    # dist 50
    ball = MockBall(500, 550)

    mode.lightning_timer = 0.0
    mode.tick(world, [ball], 0.1)

    assert ball.hp == 80.0 # took 20 damage

    events = [e for e in world.events if e[0] == "chain_lightning_strike"]
    assert len(events) == 1

if __name__ == '__main__':
    test_supercell_storm_spawn()
    test_supercell_storm_lightning()
    print("Tests passed.")
