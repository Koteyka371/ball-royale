import sys
import os
sys.path.append(os.path.abspath('src'))
import pytest
from ai.game_modes import ToxicFloodRoyaleMode

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'width': 1000, 'height': 1000, 'hazards': []})()
        self.events = []
        self.dead_balls = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x=500, y=500):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.speed = 100.0
        self.base_speed = 100.0

def test_toxic_flood_mode():
    mode = ToxicFloodRoyaleMode()
    world = MockWorld()
    b1 = MockBall(500, 500)
    b2 = MockBall(100, 100) # Ensure off platform initially if random platform is far
    balls = [b1, b2]

    mode.setup(world, balls)

    assert mode.state == "dry"
    assert len(mode.platforms) == 0
    assert len(world.arena.hazards) == 0

    # Tick down dry state
    mode.tick(world, balls, delta=10.0)

    assert mode.state == "warning"
    assert len(mode.platforms) > 0 # Spawned platform for 2 balls (max(1, 2//2) = 1 platform)
    assert len(world.arena.hazards) > 0 # Elevated platforms as hazards

    # Move b1 onto platform
    p = mode.platforms[0]
    b1.x = p["x"]
    b1.y = p["y"]

    # Move b2 away
    b2.x = p["x"] + p["radius"] + 100
    b2.y = p["y"] + p["radius"] + 100

    # Tick down warning state
    mode.tick(world, balls, delta=5.0)
    assert mode.state == "flooded"

    # Tick in flooded state
    mode.tick(world, balls, delta=1.0)

    assert b1.hp == 100.0 # B1 on platform, safe
    assert b2.hp < 100.0 # B2 in flood, takes damage
    assert b2.speed < b2.base_speed # B2 slowed

    # Kill b2
    mode.tick(world, balls, delta=10.0) # More damage
    assert not b2.alive
    assert b2.killer == "Toxic Flood"

    assert mode.state == "dry"
    assert len(mode.platforms) == 0
    assert len(world.arena.hazards) == 0
