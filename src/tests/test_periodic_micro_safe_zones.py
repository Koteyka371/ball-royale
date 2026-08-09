import pytest
import math
from unittest.mock import MagicMock
from ai.game_modes import PeriodicMicroSafeZonesMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, ev_type, data):
        self.events.append({"type": ev_type, "data": data})

class MockEntity:
    def __init__(self, id, x, y, hp=100.0, team="team1"):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.team = team
        self.alive = True
        self.ball_type = "normal"
        self.radius = 20.0

def test_periodic_micro_safe_zones():
    mode = PeriodicMicroSafeZonesMode()
    world = MockWorld()

    b1 = MockEntity(1, 150, 150)
    b2 = MockEntity(2, 500, 500)
    b3 = MockEntity(3, 850, 850)

    balls = [b1, b2, b3]
    mode.setup(world, balls)

    assert mode.state == "waiting"
    assert mode.timer == mode.spawn_interval

    # Advance time to spawn zones
    mode.tick(world, balls, delta=mode.spawn_interval)

    assert mode.state == "active"
    assert mode.timer == mode.zone_duration

    # We will manually overwrite zones to fixed positions to test physics
    mode.zones = [
        {"x": 150.0, "y": 150.0, "radius": mode.zone_initial_radius},
        {"x": 850.0, "y": 850.0, "radius": mode.zone_initial_radius}
    ]

    # Shrink to middle of duration
    mode.tick(world, balls, delta=mode.zone_duration / 2)
    # They should shrink by half
    expected_r = mode.zone_min_radius + (mode.zone_initial_radius - mode.zone_min_radius) * 0.5
    for z in mode.zones:
        assert math.isclose(z["radius"], expected_r)

    b1_initial_hp = b1.hp
    b2_initial_hp = b2.hp
    b3_initial_hp = b3.hp

    # Tick to completion (blast time)
    mode.tick(world, balls, delta=mode.zone_duration / 2)

    # At completion, b1 and b3 are exactly on the centers of zones, so they are well within min_radius (30.0 + 20.0).
    # b2 is far away (500, 500) so it should take blast damage (40.0).

    assert b1.hp == b1_initial_hp, "b1 was inside the safe zone, should take no damage"
    assert b3.hp == b3_initial_hp, "b3 was inside the safe zone, should take no damage"
    assert b2.hp == b2_initial_hp - mode.blast_damage, "b2 was outside, should take blast damage"

    assert mode.state == "waiting"
    assert mode.timer == mode.spawn_interval
    assert len(mode.zones) == 0
