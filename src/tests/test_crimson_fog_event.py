import pytest
import os
import sys
sys.path.append(os.path.abspath('src'))
from ai.game_modes import CrimsonFogEventMode, GAME_MODES

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
        self.lifesteal = 0.0

def test_crimson_fog_mode():
    assert 'crimson_fog_event' in GAME_MODES
    mode = GAME_MODES['crimson_fog_event']
    world = MockWorld()
    b = MockBall(500, 500)
    balls = [b]

    world.weekly_mutator = ''
    mode.setup(world, balls)

    assert not mode.fog_active
    assert mode.fog_timer == 20.0
    assert b.hp == 100.0
    assert getattr(b, '_crimson_fog_lifesteal_applied', False) == False

    # Fast forward to fog start
    for _ in range(20):
        mode.tick(world, balls, delta=1.0)
        b.hp = 100.0

    assert mode.fog_active
    assert b.lifesteal > 1.5
    assert getattr(b, "_crimson_fog_lifesteal_applied", False)

    # Tick inside fog
    mode.tick(world, balls, delta=1.0)
    assert b.hp == 90.0 # drain is 10.0 per second

    # Fast forward to fog end
    mode.tick(world, balls, delta=15.0) # wait, fog_duration is 15
    assert not mode.fog_active
    assert getattr(b, '_crimson_fog_lifesteal_applied', False) == False
    assert not getattr(b, "_crimson_fog_lifesteal_applied", False)
