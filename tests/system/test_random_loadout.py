import pytest
import os
import sys
sys.path.insert(0, os.path.abspath('src'))
from system.profile import ProfileManager
from system.lobby import PreGameLobby

@pytest.fixture
def temp_profile_file(tmp_path):
    file_path = tmp_path / "test_profile_random.json"
    return str(file_path)

def test_apply_random_loadout(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    pm.data["unlocked_balls"] = ["ninja", "wizard", "tank", "sniper"]
    pm.save()

    lobby = PreGameLobby()
    result = lobby.apply_random_loadout(1, pm)

    assert result is True
    assert lobby.get_trap_variant(1) in ["normal", "poison", "stun", "ricochet", "emp", "hologram", "blindness", "chain_lightning", "decoy", "mine", "warp", "siphon", "clone", "tar", "link"]
    assert lobby.selections["1_ball_type"] in ["ninja", "wizard", "tank", "sniper"]

    quests = pm.get_quests()
    assert len(quests) > 0
    assert quests[-1]["description"] == "Win a match using a Random Loadout"
    assert quests[-1]["reward"] == 300
