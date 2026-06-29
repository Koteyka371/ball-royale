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
        self.lm.update_prestige("local_player", 5)
        self.lm.update_prestige("other_player", 3)

        # Fast forward time
        self.lm.data["season_start_time"] = time.time() - LeaderboardManager.SEASON_DURATION - 1
        self.lm.check_season()

        self.assertEqual(self.lm.data["current_season"], 2)
        self.assertIn("Crown of Season 1", self.pm.data.get("cosmetics", []))
        self.assertIn("Season 1 Champion", self.pm.data.get("titles", []))
        self.assertIn("Aura of Season 1", self.pm.data.get("status_effects", []))

if __name__ == '__main__':
    unittest.main()
