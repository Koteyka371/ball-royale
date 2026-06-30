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

if __name__ == '__main__':
    unittest.main()
