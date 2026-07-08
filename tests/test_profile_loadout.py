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
    pm.save_loadout("stealth", "ninja", "poison", {"bonus_speed": 5}, cosmetic="shadow", title="The Silent", perks=["Thick Skinned", "Nimble"])

    loadout = pm.get_loadout("stealth")
    assert loadout is not None
    assert loadout["ball_type"] == "ninja"
    assert loadout["trap_variant"] == "poison"
    assert loadout["preferred_bonuses"]["bonus_speed"] == 5
    assert loadout["cosmetic"] == "shadow"
    assert loadout["title"] == "The Silent"
    assert loadout["perks"] == ["Thick Skinned", "Nimble"]

def test_default_loadout(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    pm.save_loadout("loadout1", "tank", "emp")
    pm.save_loadout("loadout2", "sniper", "stun")

    # Set and get default loadout
    assert pm.set_default_loadout("loadout2") is True
    assert pm.get_default_loadout() == "loadout2"

    lobby = PreGameLobby()
    # Apply default loadout
    assert lobby.apply_default_loadout(1, pm) is True
    assert lobby.get_trap_variant(1) == "stun"
    assert lobby.selections["1_ball_type"] == "sniper"

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
    pm.save_loadout("my_fav2", "wizard", "stun", {"bonus_damage": 3}, perks=["Heavy Hitter"])
    result = lobby.apply_loadout_to_ball(1, pm, "my_fav")

    assert result is True
    assert lobby.get_trap_variant(1) == "stun"
    assert lobby.selections["1_ball_type"] == "wizard"
    assert lobby.selections["1_preferred_bonuses"] == {"bonus_damage": 3}

    lobby.apply_loadout_to_ball(3, pm, "my_fav2")
    assert lobby.get_perks(3) == ["Heavy Hitter"]

    result2 = lobby.apply_loadout_to_ball(2, pm, "nonexistent")
    assert result2 is False


def test_loadout_sharing_code(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    pm.save_loadout("shared_setup", "warrior", "emp", {"bonus_damage": 10}, cosmetic="flame", title="The Burner")

    code = pm.generate_loadout_code("shared_setup")
    assert code is not None
    assert isinstance(code, str)
    assert len(code) > 0

    # Ensure invalid code fails gracefully
    assert pm.import_loadout_code("invalid_import", "invalid_base64_string!!!!") is False
    assert pm.get_loadout("invalid_import") is None

    # Import the code under a new name
    success = pm.import_loadout_code("imported_setup", code)
    assert success is True

    imported_loadout = pm.get_loadout("imported_setup")
    assert imported_loadout is not None
    assert imported_loadout["ball_type"] == "warrior"
    assert imported_loadout["trap_variant"] == "emp"
    assert imported_loadout["preferred_bonuses"]["bonus_damage"] == 10
    assert imported_loadout["cosmetic"] == "flame"
    assert imported_loadout["title"] == "The Burner"
