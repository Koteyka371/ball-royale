import math
import random
from ai.game_modes import GameMode, GAME_MODES

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'hazards': []})()
        self.events = []

    def add_event(self, kind, data):
        self.events.append({'type': kind, 'data': data})

class MockBall:
    def __init__(self, x, y, b_id, team):
        self.id = b_id
        self.x = x
        self.y = y
        self.radius = 20
        self.hp = 100
        self.team = team

def test_disorientation_brush():
    mode = GAME_MODES.get("disorientation_brush")
    assert mode is not None

    world = MockWorld()

    hazard = mode.hazard_class(1, 100, 100, 100, "disorientation_brush", 10.0)
    hazard.owner_id = 99
    hazard.owner_team = "A"
    world.arena.hazards.append(hazard)

    b1 = MockBall(100, 100, 1, "B") # inside, enemy
    b2 = MockBall(500, 500, 2, "B") # outside, enemy
    b3 = MockBall(100, 100, 99, "A") # inside, owner
    balls = [b1, b2, b3]

    mode.tick(world, balls, 1.0)

    # Should have generated pings and sounds for b1
    pings = [e for e in world.events if e['type'] == 'minimap_ping']
    sounds = [e for e in world.events if e['type'] == 'play_sound']

    assert len(pings) == 1
    assert len(sounds) == 1

    # Ensure they target b1
    assert pings[0]['data']['target_id'] == b1.id
    assert sounds[0]['data']['target_id'] == b1.id

    # Check timers
    assert getattr(b1, "disorientation_ping_timer", 0) == 0.1
    assert getattr(b2, "disorientation_ping_timer", 0) == 0
    assert getattr(b3, "disorientation_ping_timer", 0) == 0

    # Second tick, timer not up yet
    world.events = []
    mode.tick(world, balls, 0.05)

    assert len(world.events) == 0
    # Floating point precision
    assert abs(getattr(b1, "disorientation_ping_timer", 0) - 0.05) < 0.001
