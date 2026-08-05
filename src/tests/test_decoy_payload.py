import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.game_modes import EscortMode

class MockPayload:
    def __init__(self):
        self.ball_type = "payload"
        self.x = 100.0
        self.y = 500.0
        self.team = "Defenders"
        self.alive = True
        self.sprite = "payload_sprite.png"
        self.color = "red"
        self.scale = 1.5
        self.radius = 25.0

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_decoy_payload_spawn():
    mode = EscortMode()
    world = MockWorld()
    payload = MockPayload()

    mode.payload = payload
    balls = [payload]

    for i in range(1600):
        mode.tick(world, balls, 0.01)
        if getattr(mode, 'decoy_deployed', False):
            break

    assert getattr(mode, 'decoy_deployed', False)
    assert mode.decoy is not None
    assert mode.decoy.ball_type == "decoy_payload"
    assert mode.decoy.team == "Defenders"
    assert getattr(mode.decoy, "sprite") == "payload_sprite.png"
    assert getattr(mode.decoy, "color") == "red"
    assert getattr(mode.decoy, "scale") == 1.5
    assert getattr(mode.decoy, "radius") == 25.0
