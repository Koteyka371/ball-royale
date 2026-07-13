import pytest
from system.crowd_system import CrowdSystem
from unittest.mock import MagicMock

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, t, data):
        self.events.append((t, data))

class MockBall:
    def __init__(self, id, team="red", alive=True):
        self.id = id
        self.team = team
        self.alive = alive
        self.ball_type = "normal"
        self.x = 0
        self.y = 0

def test_large_scale_event_triggered():
    system = CrowdSystem(MockWorld())
    system.excitement_level = 0.0 # Critical threshold
    balls = [MockBall(1)]

    # Force the random to hit
    import random
    original_random = random.random
    original_choice = random.choice

    try:
        random.random = lambda: 0.001

        # Mock choice to pick closing zone
        random.choice = lambda choices: "closing_zone" if "closing_zone" in choices else choices[0]

        system.tick(balls, [], 1)

        events = [e[0] for e in system.world.events]
        assert "spawn_zone" in events
        assert system.excitement_level >= 40.0

    finally:
        random.random = original_random
        random.choice = original_choice
