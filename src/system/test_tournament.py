import unittest
import os
import time
import sys

# Add src to python path for local imports
sys.path.insert(0, os.path.abspath('src'))

from system.profile import ProfileManager
from system.tournament import TournamentManager

class TestTournament(unittest.TestCase):
    def setUp(self):
        if os.path.exists("test_profile.json"):
            os.remove("test_profile.json")
        if os.path.exists("test_tournament.json"):
            os.remove("test_tournament.json")

        self.pm = ProfileManager("test_profile.json")
        self.tm = TournamentManager("test_tournament.json", profile_manager=self.pm)

    def tearDown(self):
        if os.path.exists("test_profile.json"):
            os.remove("test_profile.json")
        if os.path.exists("test_tournament.json"):
            os.remove("test_tournament.json")

    def test_record_score(self):
        self.tm.record_score("local_player", 150)
        self.tm.record_score("local_player", 50)
        self.tm.record_score("other_player", 100)

        self.assertEqual(self.tm.data["player_scores"]["local_player"], 200)
        self.assertEqual(self.tm.data["player_scores"]["other_player"], 100)

    def test_tournament_end_awards(self):
        self.tm.record_score("local_player", 500)
        self.tm.record_score("other_player", 200)

        # Fast forward time to simulate end of tournament
        self.tm.data["tournament_start_time"] = time.time() - TournamentManager.TOURNAMENT_DURATION - 1
        self.tm.check_tournament_end()

        # Check tournament incremented and scores reset
        self.assertEqual(self.tm.data["current_tournament"], 2)
        self.assertEqual(len(self.tm.data["player_scores"]), 0)

        # Verify profile rewards
        self.assertIn("Tournament 1 Champion Skin", self.pm.data.get("cosmetics", []))
        self.assertIn("Aura of Tournament 1", self.pm.data.get("status_effects", []))

    def test_tournament_end_no_rewards_for_loser(self):
        self.tm.record_score("local_player", 100)
        self.tm.record_score("other_player", 500)

        # Fast forward time
        self.tm.data["tournament_start_time"] = time.time() - TournamentManager.TOURNAMENT_DURATION - 1
        self.tm.check_tournament_end()

        # Verify no rewards
        self.assertNotIn("Tournament 1 Champion Skin", self.pm.data.get("cosmetics", []))
        self.assertNotIn("Aura of Tournament 1", self.pm.data.get("status_effects", []))

if __name__ == '__main__':
    unittest.main()
