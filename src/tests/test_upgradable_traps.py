import pytest
from system.profile import ProfileManager
from system.lobby import PreGameLobby

def test_trap_level_upgrade():
    pm = ProfileManager("test_upgrade_traps.json")
    pm.data["skill_points"] = 100
    pm.data["trap_levels"] = {}

    # Check default level
    assert pm.get_trap_level("normal") == 1

    # Upgrade
    success = pm.upgrade_trap("normal", 50)
    assert success is True
    assert pm.get_trap_level("normal") == 2
    assert pm.data["skill_points"] == 50

    # Try upgrade without enough points
    success = pm.upgrade_trap("normal", 100)
    assert success is False
    assert pm.get_trap_level("normal") == 2
    assert pm.data["skill_points"] == 50
