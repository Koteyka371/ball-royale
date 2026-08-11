import pytest
import math
from ai.game_modes import LaserTagMode

class MockWorld:
    def __init__(self):
        self.next_id = 1
        self.arena = type('Arena', (), {'width': 1000.0, 'height': 1000.0})()
        self.projectiles = []
        self.events = []
    def add_event(self, kind, data):
        self.events.append((kind, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15.0
        self.alive = True
        self.hp = 100
        self.ball_type = "player"
        self.team = None
        self.has_been_hit = False

def test_laser_tag_mode_shoot():
    mode = LaserTagMode()
    world = MockWorld()
    b1 = MockBall(1, 100, 100)
    b2 = MockBall(2, 200, 200)
    balls = [b1, b2]

    # Tick for cooldown
    mode.tick(world, balls, 2.0)

    assert len(world.projectiles) > 0, "No projectiles spawned"
    p = world.projectiles[0]

    # Hit logic
    p.x = b2.x
    p.y = b2.y
    p.vx = 0
    p.vy = 0

    mode.tick(world, balls, 0.1)

    assert getattr(b2, "has_been_hit", False)
    assert getattr(b2, "stun_timer", 0.0) >= 3.0
    assert getattr(b2, "hp", 100) == 0
