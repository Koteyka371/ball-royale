import unittest
import time
import sys
sys.path.append('src')
from system.profile import ProfileManager
from system.leaderboard import LeaderboardManager
import os

class TestCatchup(unittest.TestCase):
    def setUp(self):
        if os.path.exists("test_profile.json"): os.remove("test_profile.json")
        if os.path.exists("test_leaderboard_catchup.json"): os.remove("test_leaderboard_catchup.json")
        self.pm = ProfileManager("test_profile.json")
        self.lm = LeaderboardManager("test_leaderboard_catchup.json", self.pm)

    def tearDown(self):
        if os.path.exists("test_profile.json"): os.remove("test_profile.json")
        if os.path.exists("test_leaderboard_catchup.json"): os.remove("test_leaderboard_catchup.json")

    def test_catchup_multiplier(self):
        # First half
        self.lm.data["season_start_time"] = time.time() - (self.lm.SEASON_DURATION * 0.1)
        self.lm.save()
        self.assertEqual(self.pm._get_catchup_multiplier(), 1.0)

        # Second half
        self.lm.data["season_start_time"] = time.time() - (self.lm.SEASON_DURATION * 0.6)
        self.lm.save()
        self.assertEqual(self.pm._get_catchup_multiplier(), 1.25)

        # Final quarter
        self.lm.data["season_start_time"] = time.time() - (self.lm.SEASON_DURATION * 0.9)
        self.lm.save()
        self.assertEqual(self.pm._get_catchup_multiplier(), 1.5)

    def test_add_skill_points_catchup(self):
        self.lm.data["season_start_time"] = time.time() - (self.lm.SEASON_DURATION * 0.9)
        self.lm.save()
        self.pm.add_skill_points(100)
        self.assertEqual(self.pm.data["skill_points"], 150)

if __name__ == '__main__':
    unittest.main()
