import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x, y):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 100.0
        self.vy = 100.0
        self.radius = 15.0
        self.alive = True
        self.ball_type = "warrior"
        self.is_dashing = False
        self.skill_timer = 0.0
        self.dash_cooldown = 0.0
        self.random_teleport_cooldown = 0.0

def test_random_teleport_dash_mode(monkeypatch):
    import random

    # Force random to always trigger teleport
    monkeypatch.setattr(random, "random", lambda: 0.1)
    monkeypatch.setattr(random, "uniform", lambda a, b: a if b > 10 else 0) # 150 radius, 0 angle

    mode = GAME_MODES["random_teleport_dash"]
    world = MockWorld()

    # Test 1: No dash, no teleport
    b = MockBall(500.0, 500.0)
    mode.tick(world, [b], 0.016)
    assert b.x == 500.0
    assert b.y == 500.0
    assert not world.events

    # Test 2: Dashing triggers teleport
    b = MockBall(500.0, 500.0)
    b.is_dashing = True
    mode.tick(world, [b], 0.016)
    assert b.x == 650.0  # 500 + 150 * cos(0)
    assert b.y == 500.0  # 500 + 150 * sin(0)
    assert b.vx == 0.0
    assert b.vy == 0.0
    assert b.random_teleport_cooldown > 0
    assert len(world.events) == 1
    assert world.events[0][0] == "visual_effect"
    assert world.events[0][1]["type"] == "teleport"

    # Test 3: Skill usage triggers teleport
    world.events.clear()
    b = MockBall(500.0, 500.0)
    b._prev_teleport_skill_timer = 0.0
    b.skill_timer = 2.0
    mode.tick(world, [b], 0.016)
    assert b.x == 650.0
    assert b.y == 500.0
    assert len(world.events) == 1

    # Test 4: Dash cooldown triggers teleport
    world.events.clear()
    b = MockBall(500.0, 500.0)
    b._prev_teleport_dash_cooldown = 0.0
    b.dash_cooldown = 2.0
    mode.tick(world, [b], 0.016)
    assert b.x == 650.0
    assert b.y == 500.0
    assert len(world.events) == 1
