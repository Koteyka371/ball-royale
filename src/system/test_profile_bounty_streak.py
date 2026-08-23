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

def test_bounty_streak_multiplier(pm):
    # Place 3 bounties consecutively
    pm.place_player_bounty("enemy_1", 10, "prestige_tokens")
    pm.place_player_bounty("enemy_2", 10, "prestige_tokens")
    pm.place_player_bounty("enemy_3", 10, "prestige_tokens")

    assert pm.data.get("bounty_streak") == 3
    assert pm.data["prestige_tokens"] == 70

    # Claim one of them
    pm.claim_player_bounty("enemy_1", "local_player")

    # Base reward is 10 * 3 = 30. Multiplier is 3 (streak). Total = 90
    assert pm.data["prestige_tokens"] == 70 + 90
    assert pm.data.get("bounty_streak", 0) == 0

def test_bounty_streak_other_claim(pm):
    # Place 2 bounties
    pm.place_player_bounty("enemy_1", 10, "prestige_tokens")
    pm.place_player_bounty("enemy_2", 10, "prestige_tokens")

    assert pm.data.get("bounty_streak") == 2

    # Claim someone else's bounty (placed by other)
    pm.data["active_bounties"]["enemy_4"] = {"reward": 10, "placer": "other_player", "currency": "prestige_tokens"}

    # Claim it
    pm.claim_player_bounty("enemy_4", "local_player")

    # Reward should be 10 * 0.5 = 5. Multiplied by streak 2? Or is streak only for own bounties?
    # "reward is multiplied by the streak" -> 5 * 2 = 10
    # Let's say we apply streak to any claim by local_player
    # Wait, the prompt says "When they finally claim one, the reward is multiplied by the streak, encouraging risky investments for massive payoffs."
