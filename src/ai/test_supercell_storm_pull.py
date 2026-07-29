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
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0

def test_supercell_storm_pull():
    mode = GAME_MODES["supercell_storm"]
    world = MockWorld()
    mode.setup(world, [])

    # Spawn tornado
    mode.wind_timer = 0.0
    mode.tick(world, [], 0.1)

    assert len(world.arena.hazards) == 1
    tornado = world.arena.hazards[0]
    tornado.x = 500
    tornado.y = 500
    tornado.radius = 100.0

    # Place a ball outside but within outer radius
    # Distance: 50 from center
    ball = MockBall(550, 500)

    initial_vx = ball.vx
    initial_vy = ball.vy

    mode.tick(world, [ball], 0.1)

    # Ball should have vx pulling it towards center (500)
    # Center is at x=500, ball is at 550, so dx = -50.
    # Pull should make vx negative.
    assert ball.vx < initial_vx
    assert ball.vy == initial_vy

if __name__ == '__main__':
    test_supercell_storm_pull()
    print("Tests passed.")
