import pytest
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


def test_default_loadout(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    pm.save_loadout("main", "basic", "normal")
    pm.save_loadout("alt", "sniper", "poison")

    assert pm.get_default_loadout_name() is None
    assert pm.get_default_loadout() is None

    res = pm.set_default_loadout("main")
    assert res is True
    assert pm.get_default_loadout_name() == "main"
    assert pm.get_default_loadout()["ball_type"] == "basic"

    res_bad = pm.set_default_loadout("missing")
    assert res_bad is False

def test_rename_loadout(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    pm.save_loadout("old_name", "healer", "emp")
    pm.set_default_loadout("old_name")

    res = pm.rename_loadout("old_name", "new_name")
    assert res is True
    assert "old_name" not in pm.get_all_loadouts()
    assert "new_name" in pm.get_all_loadouts()
    assert pm.get_default_loadout_name() == "new_name"
    assert pm.get_loadout("new_name")["ball_type"] == "healer"

def test_delete_default_loadout(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    pm.save_loadout("main", "basic", "normal")
    pm.set_default_loadout("main")

    pm.delete_loadout("main")
    assert pm.get_default_loadout_name() is None


def test_apply_default_loadout_to_lobby(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    pm.save_loadout("auto_fav", "trickster", "poison", {"bonus_hp": 2})
    pm.set_default_loadout("auto_fav")

    lobby = PreGameLobby()
    result = lobby.apply_default_loadout(3, pm)

    assert result is True
    assert lobby.get_trap_variant(3) == "poison"
    assert lobby.selections["3_ball_type"] == "trickster"
    assert lobby.selections["3_preferred_bonuses"] == {"bonus_hp": 2}

    # No default loadout set
    pm2 = ProfileManager(temp_profile_file + "_2")
    lobby2 = PreGameLobby()
    result2 = lobby2.apply_default_loadout(4, pm2)
    assert result2 is False
