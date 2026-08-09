import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from ai.game_modes import GameMode

class MockBall:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def test_legendary_kill_particles():
    mode = GameMode()

    dead_ball = MockBall(id=1, x=100.0, y=200.0, kill_bounty=0)
    killer = MockBall(id=2, skin="legendary", kill_bounty=0, gold=0)

    class MockWorld:
        def __init__(self):
            self.events = []
            self.profile_manager = None
        def add_event(self, kind, data):
            self.events.append((kind, data))

    world = MockWorld()

    # Simulate kill
    mode.on_ball_died(world, dead_ball, killer=killer)

    # Verify event was emitted
    assert any(e[0] == "visual_effect" and e[1].get("type") == "legendary_kill_particles" and e[1].get("x") == 100.0 and e[1].get("y") == 200.0 for e in world.events), "Legendary particles event not found"

def test_normal_kill_particles():
    mode = GameMode()

    dead_ball = MockBall(id=1, x=100.0, y=200.0, kill_bounty=0)
    killer = MockBall(id=2, skin="default", kill_bounty=0, gold=0)

    class MockWorld:
        def __init__(self):
            self.events = []
            self.profile_manager = None
        def add_event(self, kind, data):
            self.events.append((kind, data))

    world = MockWorld()

    # Simulate kill
    mode.on_ball_died(world, dead_ball, killer=killer)

    # Verify event was NOT emitted
    assert not any(e[0] == "visual_effect" and e[1].get("type") == "legendary_kill_particles" for e in world.events), "Legendary particles event should not be emitted for normal skin"
