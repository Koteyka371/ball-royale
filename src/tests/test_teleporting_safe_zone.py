import pytest
from ai.game_modes import GameMode, TeleportingSafeZoneMode
import math

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, x, y, id="p1"):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.id = id

def test_teleporting_safe_zone_mode():
    mode = TeleportingSafeZoneMode()
    world = MockWorld()
    balls = [MockBall(500, 500)]

    mode.setup(world, balls)
    assert mode.zone_x == 500.0
    assert mode.zone_y == 500.0

    # Inside zone
    mode.tick(world, balls, delta=1.0)
    assert balls[0].hp == 100.0

    # Outside zone
    balls[0].x = 100.0
    balls[0].y = 100.0
    mode.tick(world, balls, delta=1.0)
    assert balls[0].hp == 85.0

    # Teleport
    mode.teleport_timer = 9.9
    mode.tick(world, balls, delta=0.2)
    assert mode.teleport_timer < 1.0
    assert len(world.events) > 0
    assert world.events[0][0] == "zone_teleport"
