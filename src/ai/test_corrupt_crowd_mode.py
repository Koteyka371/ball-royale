import pytest
from ai.game_modes import CorruptCrowdEventMode
from system.crowd_system import CrowdSystem
from unittest.mock import MagicMock

class MockProfileManager:
    def __init__(self):
        self.data = {"skill_points": 100, "prestige_tokens": 5}

class MockWorld:
    def __init__(self):
        self.events = []
        self.profile_manager = MockProfileManager()
        self.crowd_system = CrowdSystem(self)

    def get_profile_manager(self):
        return self.profile_manager

    def add_event(self, t, data):
        self.events.append((t, data))

def test_corrupt_crowd_event_mode():
    world = MockWorld()
    mode = CorruptCrowdEventMode()

    # Tick once to start
    mode.tick(world, [], 0.016)
    assert world.crowd_system.corruptibility_level == 1.0

    # Fast forward to trigger fluctuation
    mode.fluctuation_timer = 0
    mode.tick(world, [], 0.016)

    # Level should have changed
    assert world.crowd_system.corruptibility_level != 1.0
    assert 0.1 <= world.crowd_system.corruptibility_level <= 2.5

    # Fast forward to end
    mode.event_timer = 0
    mode.tick(world, [], 0.016)

    # Should revert back
    assert world.crowd_system.corruptibility_level == 1.0
    assert mode.completed == True

def test_crowd_system_bribe_cost():
    world = MockWorld()
    system = world.crowd_system
    system.active_vote = {"type": "spawn_hazard", "options": ["lava"]}
    system.votes = {"lava": 0}

    # Standard cost is 50
    assert world.profile_manager.data["skill_points"] == 100

    # Bribe
    system.player_bribe_vote("player1", "skew", "lava")
    assert world.profile_manager.data["skill_points"] == 50
    assert system.votes["lava"] == 5

    # Cheap corruptibility
    system.corruptibility_level = 0.5
    system.player_bribe_vote("player1", "skew", "lava")

    # Cost should be 25
    assert world.profile_manager.data["skill_points"] == 25
    assert system.votes["lava"] == 10

    # Expensive corruptibility
    system.corruptibility_level = 2.0
    # Current SP is 25, need 100. Need 2 PT, only have 1 PT
    world.profile_manager.data["prestige_tokens"] = 1
    result = system.player_bribe_vote("player1", "skew", "lava")
    assert not result
