import unittest
import os
import time
from system.profile import ProfileManager
from system.leaderboard import LeaderboardManager

class TestLeaderboard(unittest.TestCase):
    def setUp(self):
        if os.path.exists("test_profile.json"):
            os.remove("test_profile.json")
        if os.path.exists("test_leaderboard.json"):
            os.remove("test_leaderboard.json")

        self.pm = ProfileManager("test_profile.json")
        self.lm = LeaderboardManager("test_leaderboard.json", profile_manager=self.pm)

    def tearDown(self):
        if os.path.exists("test_profile.json"):
            os.remove("test_profile.json")
        if os.path.exists("test_leaderboard.json"):
            os.remove("test_leaderboard.json")

    def test_season_end(self):
        # Create 105 players
        for i in range(105):
            self.lm.update_prestige(f"player_{i}", i)

        # Give local_player enough prestige to be in top 100 but not #1
        self.lm.update_prestige("local_player", 50)

        # Fast forward time
        self.lm.data["season_start_time"] = time.time() - LeaderboardManager.SEASON_DURATION - 1
        self.lm.check_season()

        self.assertEqual(self.lm.data["current_season"], 2)
        self.assertIn("Crown of Genesis", self.pm.data.get("cosmetics", []))
        self.assertIn("Genesis Champion", self.pm.data.get("titles", []))
        self.assertIn("Aura of Genesis", self.pm.data.get("status_effects", []))

    def test_season_end_not_top_100(self):
        # Create 105 players with higher prestige
        for i in range(105):
            self.lm.update_prestige(f"player_{i}", i + 10)

        # Give local_player lower prestige (not in top 100)
        self.lm.update_prestige("local_player", 5)

        # Fast forward time
        self.lm.data["season_start_time"] = time.time() - LeaderboardManager.SEASON_DURATION - 1
        self.lm.check_season()

        self.assertEqual(self.lm.data["current_season"], 2)
        self.assertNotIn("Crown of Genesis", self.pm.data.get("cosmetics", []))
        self.assertNotIn("Genesis Champion", self.pm.data.get("titles", []))
        self.assertNotIn("Aura of Genesis", self.pm.data.get("status_effects", []))

    def test_record_loadout_win(self):
        self.lm.record_loadout_win("code1", is_win=True)
        self.lm.record_loadout_win("code1", is_win=False)
        self.lm.record_loadout_win("code2", is_win=True)
        self.lm.record_loadout_win("code3", is_win=False)

        loadouts = self.lm.data.get("loadouts", {})
        self.assertIn("code1", loadouts)
        self.assertEqual(loadouts["code1"]["uses"], 2)
        self.assertEqual(loadouts["code1"]["wins"], 1)

        self.assertIn("code2", loadouts)
        self.assertEqual(loadouts["code2"]["uses"], 1)
        self.assertEqual(loadouts["code2"]["wins"], 1)

        self.assertIn("code3", loadouts)
        self.assertEqual(loadouts["code3"]["uses"], 1)
        self.assertEqual(loadouts["code3"]["wins"], 0)

    def test_get_top_loadouts(self):
        # Code 1: 10 uses, 5 wins (50%)
        for _ in range(5): self.lm.record_loadout_win("code1", is_win=True)
        for _ in range(5): self.lm.record_loadout_win("code1", is_win=False)

        # Code 2: 2 uses, 2 wins (100%) - Will be ranked lower than Code 1 because uses is the primary sort key
        for _ in range(2): self.lm.record_loadout_win("code2", is_win=True)

        # Code 3: 15 uses, 3 wins (20%) - High uses, so should be top
        for _ in range(3): self.lm.record_loadout_win("code3", is_win=True)
        for _ in range(12): self.lm.record_loadout_win("code3", is_win=False)

        top = self.lm.get_top_loadouts()
        self.assertEqual(len(top), 3)
        self.assertEqual(top[0]["code"], "code3") # 15 uses
        self.assertEqual(top[1]["code"], "code1") # 10 uses
        self.assertEqual(top[2]["code"], "code2") # 2 uses

if __name__ == '__main__':
    unittest.main()
