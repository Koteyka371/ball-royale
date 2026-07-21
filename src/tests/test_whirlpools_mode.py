import sys
import os
sys.path.append(os.path.abspath('src'))
import pytest
from ai.game_modes import GAME_MODES

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'width': 1000, 'height': 1000, 'hazards': []})()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x=500, y=500):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.speed = 100.0
        self.base_speed = 100.0

    def take_damage(self, amount):
        self.hp -= amount

def test_whirlpools_mode():
    mode = GAME_MODES.get('whirlpools')
    assert mode is not None

    world = MockWorld()
    b1 = MockBall(500, 500)
    balls = [b1]

    mode.setup(world, balls)
    assert len(mode.whirlpools) == 0

    # Tick to spawn a whirlpool
    mode.tick(world, balls, delta=6.0)

    assert len(mode.whirlpools) == 1
    assert len(world.arena.hazards) == 1

    w = mode.whirlpools[0]

    # Move ball into pull range but outside suck radius
    b1.x = w.x + 100.0
    b1.y = w.y
    b1.vx = 0.0
    b1.vy = 0.0

    mode.tick(world, balls, delta=1.0)

    # Ball should be pulled towards center (negative x velocity since it's at w.x + 100)
    assert b1.vx < 0.0

    # Move ball into center (suck_radius)
    b1.x = w.x
    b1.y = w.y
    b1.vx = 0.0
    b1.vy = 0.0
    b1.hp = 100.0
    b1.speed = 100.0

    mode.tick(world, balls, delta=1.0)

    # Should take damage
    assert b1.hp < 100.0
    # Should be slowed down
    assert b1.speed < b1.base_speed

    # Tick to expire the whirlpool
    w.duration = 0.1
    mode.tick(world, balls, delta=0.2)

    assert len(mode.whirlpools) == 0
    assert len(world.arena.hazards) == 0
