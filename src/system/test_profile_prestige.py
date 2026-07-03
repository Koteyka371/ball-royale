import pytest
import os
import sys
sys.path.insert(0, os.path.abspath('src'))
from system.profile import ProfileManager

@pytest.fixture
def temp_profile_file(tmp_path):
    return str(tmp_path / "test_profile_prestige.json")

def test_prestige_milestones(temp_profile_file):
    pm = ProfileManager(temp_profile_file)

    # Setup mock profile capable of prestige
    pm.data["unlocked_balls"] = ["basic"] * pm.TOTAL_BALLS
    pm.data["bonuses"] = {"bonus_hp": 10, "bonus_speed": 10, "bonus_damage": 10}

    # Test normal prestige
    pm.data["prestige_level"] = 3
    pm.save()
    assert pm.do_prestige() is True
    assert pm.data["prestige_level"] == 4
    assert "Prestige V Champion" not in pm.data["titles"]

    # Setup again
    pm.data["unlocked_balls"] = ["basic"] * pm.TOTAL_BALLS
    pm.data["bonuses"] = {"bonus_hp": 10, "bonus_speed": 10, "bonus_damage": 10}

    # Test Prestige 5 Milestone
    assert pm.do_prestige() is True
    assert pm.data["prestige_level"] == 5
    assert "Prestige V Champion" in pm.data["titles"]
    assert "prestige_aura_gold" in pm.data["cosmetics"]
    assert "prestige_master" in pm.data["unlocked_balls"]

    # Fast forward to prestige 9
    pm.data["prestige_level"] = 9
    pm.data["unlocked_balls"] = ["basic"] * pm.TOTAL_BALLS
    pm.data["bonuses"] = {"bonus_hp": 10, "bonus_speed": 10, "bonus_damage": 10}

    # Test Prestige 10 Milestone
    assert pm.do_prestige() is True
    assert pm.data["prestige_level"] == 10
    assert "Prestige X Grandmaster" in pm.data["titles"]
    assert "prestige_aura_diamond" in pm.data["cosmetics"]
    assert "prestige_grandmaster" in pm.data["unlocked_balls"]
