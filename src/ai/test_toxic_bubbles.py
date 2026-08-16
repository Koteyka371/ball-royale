import pytest
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self, width=1000, height=1000):
        self.width = width
        self.height = height

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.weather_immunity_timer = 0.0

def test_toxic_bubbles_damage_outside():
    assert 'toxic_bubbles' in GAME_MODES
    mode = GAME_MODES['toxic_bubbles']
    world = MockWorld()

    ball_safe = MockBall(1, 500, 500)
    ball_danger = MockBall(2, 50, 50)
    balls = [ball_safe, ball_danger]

    # We don't want random bubbles to accidentally cover our danger ball,
    # so we'll setup and then override the bubbles manually for the test.
    mode.setup(world, balls)

    # Force one bubble exactly at ball_safe's location
    mode.bubbles = [{
        "x": 500.0,
        "y": 500.0,
        "vx": 0.0,
        "vy": 0.0,
        "radius": 100.0,
        "timer": 10.0,
        "collapsing": False
    }]

    mode.tick(world, balls, delta=1.0)

    # ball_safe is exactly at the bubble center, should take no damage
    assert ball_safe.hp == 100.0

    # ball_danger is far away, should take 25.0 damage
    assert ball_danger.hp == 75.0

def test_toxic_bubbles_lethal_damage():
    mode = GAME_MODES['toxic_bubbles']
    world = MockWorld()
    ball_danger = MockBall(1, 50, 50)
    ball_danger.hp = 10.0 # Will die in one tick of 25.0 damage

    mode.setup(world, [ball_danger])
    mode.bubbles = [] # No bubbles

    mode.tick(world, [ball_danger], delta=1.0)

    assert ball_danger.hp == 0.0
    assert ball_danger.alive == False
    assert ball_danger.id in world.dead_balls

    death_event = next((e for e in world.events if e[0] == "ball_died"), None)
    assert death_event is not None
    assert death_event[1]["reason"] == "toxic_environment"
