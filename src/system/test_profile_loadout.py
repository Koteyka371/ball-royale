import pytest  # type: ignore
import os
import sys
sys.path.insert(0, os.path.abspath('src'))
from system.profile import ProfileManager
from system.lobby import PreGameLobby

@pytest.fixture
def temp_profile_file(tmp_path):
    file_path = tmp_path / "test_profile.json"
    return str(file_path)

def test_save_and_get_loadout(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    pm.save_loadout("stealth", "ninja", "poison", {"bonus_speed": 5})

    loadout = pm.get_loadout("stealth")
    assert loadout is not None
    assert loadout["ball_type"] == "ninja"
    assert loadout["trap_variant"] == "poison"
    assert loadout["preferred_bonuses"]["bonus_speed"] == 5

def test_get_all_loadouts(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    pm.save_loadout("l1", "sniper", "normal", {})
    pm.save_loadout("l2", "tank", "emp", {})

    all_l = pm.get_all_loadouts()
    assert len(all_l) == 2
    assert "l1" in all_l
    assert "l2" in all_l

def test_delete_loadout(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    pm.save_loadout("temp", "basic", "normal", {})
    assert pm.get_loadout("temp") is not None

    result = pm.delete_loadout("temp")
    assert result is True
    assert pm.get_loadout("temp") is None

    result2 = pm.delete_loadout("nonexistent")
    assert result2 is False

def test_apply_loadout_to_lobby(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    pm.save_loadout("my_fav", "wizard", "stun", {"bonus_damage": 3})

    lobby = PreGameLobby()
    result = lobby.apply_loadout_to_ball(1, pm, "my_fav")

    assert result is True
    assert lobby.get_trap_variant(1) == "stun"
    assert lobby.selections["1_ball_type"] == "wizard"
    assert lobby.selections["1_preferred_bonuses"] == {"bonus_damage": 3}

    result2 = lobby.apply_loadout_to_ball(2, pm, "nonexistent")
    assert result2 is False
