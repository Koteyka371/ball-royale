import pytest
import sys
import os
from unittest.mock import MagicMock

# Add src to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.game_modes import WeaponCollectionMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_name, data):
        self.events.append((event_name, data))

class MockBall:
    def __init__(self, ball_id, x, y):
        self.id = ball_id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.active_skill = "fireball"
        self.alive = True
        self.ball_type = "player"

def test_weapon_collection_setup():
    mode = WeaponCollectionMode()
    world = MockWorld()

    b1 = MockBall(1, 100, 100)
    b2 = MockBall(2, 200, 200)

    # Cache the original damage
    b1_damage = b1.damage

    mode.setup(world, [b1, b2])

    assert b1.active_skill is None
    assert b2.active_skill is None
    # Just verify damage didn't drop to 0
    assert b1.damage > 0.0

def test_weapon_collection_pickup():
    mode = WeaponCollectionMode()
    world = MockWorld()

    b1 = MockBall(1, 100, 100)
    mode.setup(world, [b1])

    # Spawn a weapon
    mode.tick(world, [b1], delta=4.0)

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]

    # Move ball to weapon
    b1.x = hazard.x
    b1.y = hazard.y

    mode.tick(world, [b1], delta=0.016)

    # Weapon should be collected and active_skill updated
    assert hazard.active is False
    assert b1.active_skill is not None
    assert b1.active_skill in [
        "fireball",
        "explosion",
        "deployable_thumper",
        "deployable_thin_hazard_line",
        "laser_tripwire",
        "mind_control",
        "ground_pound",
        "orbital_shield",
        "phase_through",
        "repel_burst"
    ]
