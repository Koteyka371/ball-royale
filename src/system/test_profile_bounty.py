import pytest
import os
import sys
sys.path.insert(0, os.path.abspath('src'))
from system.profile import ProfileManager

@pytest.fixture
def pm(tmp_path):
    pm = ProfileManager(str(tmp_path / "test.json"))
    pm.data["prestige_tokens"] = 100
    pm.data["skill_points"] = 100
    pm.save()
    return pm

def test_place_bounty(pm):
    assert pm.place_player_bounty("enemy_1", 20, "skill_points") is True
    assert pm.data["skill_points"] == 80

    bounties = pm.get_player_bounties()
    assert "enemy_1" in bounties
    assert bounties["enemy_1"]["reward"] == 20
    assert bounties["enemy_1"]["currency"] == "skill_points"
    assert bounties["enemy_1"]["placer"] == "local_player"

def test_claim_bounty_by_placer(pm):
    pm.place_player_bounty("enemy_2", 10, "prestige_tokens")
    assert pm.data["prestige_tokens"] == 90

    pm.claim_player_bounty("enemy_2", "local_player")
    bounties = pm.get_player_bounties()
    assert bounties["enemy_2"]["reward"] == 0
    assert pm.data["prestige_tokens"] == 90 + 30 # 3x return

def test_claim_bounty_by_other(pm):
    pm.place_player_bounty("enemy_3", 10, "prestige_tokens")
    assert pm.data["prestige_tokens"] == 90

    pm.claim_player_bounty("enemy_3", "enemy_other")
    # If placed by local_player and claimed by enemy_other, local_player gets half
    assert pm.data["prestige_tokens"] == 90 + 5
def test_claim_bounty_by_local_player_placed_by_other(pm):
    # Manually place bounty by another player
    pm.data["active_bounties"] = {}
    pm.data["active_bounties"]["enemy_4"] = {"reward": 10, "placer": "other_player", "currency": "prestige_tokens"}
    pm.save()

    assert pm.data["prestige_tokens"] == 100
    pm.claim_player_bounty("enemy_4", "local_player")
    assert pm.data["prestige_tokens"] == 100 + 5 # claimer gets half, placer is not local_player
