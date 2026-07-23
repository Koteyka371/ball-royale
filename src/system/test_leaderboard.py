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

    def test_record_nemesis_defeat_active_event(self):
        self.lm.set_nemesis_event_active(True)
        self.assertTrue(self.lm.is_nemesis_event_active())

        initial_tokens = self.pm.data.get("prestige_tokens", 0)

        self.lm.record_nemesis_defeat("local_player", "enemy_1")

        # Check rivalry recorded
        self.assertEqual(self.lm.data["nemesis_rivalries"]["enemy_1_vs_local_player"], 1)

        # Check rewards
        self.assertIn("Nemesis Slayer", self.pm.data.get("cosmetics", []))
        self.assertIn("Rivalry Champion", self.pm.data.get("titles", []))
        self.assertEqual(self.pm.data.get("prestige_tokens", 0), initial_tokens + 10)

    def test_record_nemesis_defeat_inactive_event(self):
        self.lm.set_nemesis_event_active(False)
        self.assertFalse(self.lm.is_nemesis_event_active())

        initial_tokens = self.pm.data.get("prestige_tokens", 0)

        self.lm.record_nemesis_defeat("local_player", "enemy_1")

        # Check rivalry recorded
        self.assertEqual(self.lm.data["nemesis_rivalries"]["enemy_1_vs_local_player"], 1)

        # Check NO rewards
        self.assertNotIn("Nemesis Slayer", self.pm.data.get("cosmetics", []))
        self.assertNotIn("Rivalry Champion", self.pm.data.get("titles", []))
        self.assertEqual(self.pm.data.get("prestige_tokens", 0), initial_tokens)

    def test_get_top_rivalries(self):
        self.lm.record_nemesis_defeat("player_a", "player_b")
        self.lm.record_nemesis_defeat("player_b", "player_a") # Same rivalry
        self.lm.record_nemesis_defeat("player_c", "player_d")

        top = self.lm.get_top_rivalries()
        self.assertEqual(len(top), 2)

        # "player_a_vs_player_b" has 2 defeats, so it should be first
        self.assertEqual(top[0]["rivalry"], "player_a_vs_player_b")
        self.assertEqual(top[0]["defeats"], 2)

        self.assertEqual(top[1]["rivalry"], "player_c_vs_player_d")
        self.assertEqual(top[1]["defeats"], 1)











    def test_viewer_loyalty(self):
        self.lm.record_viewer_loyalty("viewer_1", 10)
        self.assertEqual(self.lm.get_viewer_badge("viewer_1"), "")

        self.lm.record_viewer_loyalty("viewer_1", 10)
        self.assertEqual(self.lm.get_viewer_badge("viewer_1"), "⭐")

        self.lm.record_viewer_loyalty("viewer_1", 30)
        self.assertEqual(self.lm.get_viewer_badge("viewer_1"), "👑")

        self.assertEqual(self.lm.get_viewer_badge("unknown_viewer"), "")

    def test_store_and_get_top_player_replay(self):
        replay_data = {"frames": [{"tick": 1, "entities": []}], "version": "1.0"}

        self.lm.store_top_player_replay("player_1", replay_data)

        self.assertIn("top_replays", self.lm.data)
        self.assertIn("player_1", self.lm.data["top_replays"])

        fetched_replay = self.lm.get_top_player_replay("player_1")
        self.assertIsNotNone(fetched_replay)
        self.assertEqual(fetched_replay["version"], "1.0")
        self.assertEqual(len(fetched_replay["frames"]), 1)

        # Check non-existent player
        self.assertIsNone(self.lm.get_top_player_replay("player_2"))

    def test_record_match_replay_top_10(self):
        from system.replay import ReplaySystem
        # Give player_1 enough prestige
        self.lm.update_prestige("player_1", 100)
        self.lm.update_prestige("player_2", 10)

        replay = ReplaySystem()
        replay.start_recording()
        replay.record_frame(1, [{"id": 1}], [])
        replay.stop_recording()

        self.lm.record_match_replay("player_1", replay)

        replays = self.lm.get_available_replays()
        self.assertIn("player_1", replays)

        fetched = self.lm.get_top_player_replay("player_1")
        self.assertIsNotNone(fetched)
        self.assertEqual(len(fetched["frames"]), 1)

        # player_2 not in top 1 (wait, they are top 2 since there are only 2 players)
        # Let's add 10 more players with higher prestige
        for i in range(3, 13):
            self.lm.update_prestige(f"player_{i}", 50)

        # player_2 is now not in top 10
        self.lm.record_match_replay("player_2", replay)
        replays = self.lm.get_available_replays()
        self.assertNotIn("player_2", replays)

if __name__ == '__main__':
    unittest.main()
