import pytest
from ai.game_modes import EarthquakeMode
from ai.action import Action
import random

def test_earthquake_mode_random_impulses():
    class MockArena:
        def __init__(self):
            self.hazards = []
            self.items = []

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()
            self.events = []
            self.dead_balls = []

        def add_event(self, event_type, data):
            self.events.append({'type': event_type, 'data': data})

    class MockBall:
        def __init__(self, hp=100, x=0.0, y=0.0, vx=0.0, vy=0.0):
            self.hp = hp
            self.x = x
            self.y = y
            self.vx = vx
            self.vy = vy
            self.alive = True

    random.seed(42)
    mode = EarthquakeMode()
    world = MockWorld()

    b1 = MockBall()
    balls = [b1]

    # Trigger earthquake
    mode.timer = 11.0
    # force random < 0.2*delta by mocking random.random temporarily
    orig_random = random.random
    random.random = lambda: 0.0
    mode.tick(world, balls, 0.016)
    random.random = orig_random

    assert mode.is_shaking == True

    # Apply impulses
    prev_vx, prev_vy = b1.vx, b1.vy
    mode.tick(world, balls, 0.016)

    # Check if impulses were applied
    assert b1.vx != prev_vx or b1.vy != prev_vy
