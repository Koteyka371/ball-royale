import pytest
import math
import random
from unittest.mock import MagicMock
from ai.game_modes import UnstablePortalsEventMode

class MockArena:
    def __init__(self):
        self.width = 800
        self.height = 600

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, event_data):
        self.events.append((event_type, event_data))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.visible = True

    def take_damage(self, damage):
        self.hp -= damage

def test_unstable_portal_overload():
    mode = UnstablePortalsEventMode()
    world = MockWorld()

    # Spawn a portal
    mode.portals.append({
        "x": 400.0,
        "y": 300.0,
        "timer": 5.0,
        "active": True,
        "charging": False,
        "charge_timer": 0.0,
        "sucked_balls": []
    })
    portal = mode.portals[0]

    # Create 3 balls near portal
    b1 = MockBall(1, 400.0, 305.0)
    b2 = MockBall(2, 400.0, 295.0)
    b3 = MockBall(3, 405.0, 300.0)
    balls = [b1, b2, b3]

    # Tick to suck balls in
    mode.tick(world, balls, delta=0.1)

    # The first ball enters, starts charging, other balls pulled/sucked next tick
    for i in range(10):
        mode.tick(world, balls, delta=0.1)

    # The portal shouldn't wait full 2.0s if overloaded
    # Wait, we need them all inside. In our logic, as soon as a ball enters, it's sucked.
    # The overloaded condition is sucked_count >= 3
    # When it overloads, the blast happens with multiplied damage (20 * 3 = 60)
    assert not portal["active"]

    # Find explosion event
    explosion = None
    for event_type, event_data in world.events:
        if event_type == "explosion":
            explosion = event_data
            break

    assert explosion is not None
    assert explosion["radius"] == 450.0  # 150 * 3
    assert explosion["damage"] == 60.0   # 20 * 3

    # Check ball damage
    assert b1.hp <= 40.0
    assert b2.hp <= 40.0
    assert b3.hp <= 40.0

if __name__ == "__main__":
    test_unstable_portal_overload()
    print("Test passed")
