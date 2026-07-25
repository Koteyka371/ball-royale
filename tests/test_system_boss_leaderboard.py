import unittest
import os
from system.leaderboard import LeaderboardManager
from system.guild import GuildManager

class TestBossLeaderboard(unittest.TestCase):
    def setUp(self):
        if os.path.exists("test_leaderboard_boss.json"):
            os.remove("test_leaderboard_boss.json")
        if os.path.exists("test_guilds_boss.json"):
            os.remove("test_guilds_boss.json")

        self.lm = LeaderboardManager("test_leaderboard_boss.json")
        self.gm = GuildManager("test_guilds_boss.json")

    def tearDown(self):
        if os.path.exists("test_leaderboard_boss.json"):
            os.remove("test_leaderboard_boss.json")
        if os.path.exists("test_guilds_boss.json"):
            os.remove("test_guilds_boss.json")

    def test_process_guild_boss_leaderboard(self):
        self.gm.create_guild("Alpha", "p1")
        self.gm.create_guild("Beta", "p2")
        self.gm.create_guild("Gamma", "p3")
        self.gm.create_guild("Delta", "p4")
        self.gm.create_guild("Epsilon", "p5")

        week_id = "week_42"

        # Tier requirements: Tier 1=1000, Tier 2=5000, Tier 3=10000
        tier_reqs = {1: 1000, 2: 5000, 3: 10000}

        # Alpha cleared T3 with 12000 dmg
        self.gm.record_boss_damage("Alpha", 12000, week_id, tier=3)
        # Beta cleared T2 with 6000 dmg
        self.gm.record_boss_damage("Beta", 6000, week_id, tier=2)
        # Gamma cleared T2 with 5500 dmg
        self.gm.record_boss_damage("Gamma", 5500, week_id, tier=2)
        # Delta cleared T1 with 2000 dmg
        self.gm.record_boss_damage("Delta", 2000, week_id, tier=1)
        # Epsilon did not clear any tier (only 500 dmg on T1)
        self.gm.record_boss_damage("Epsilon", 500, week_id, tier=1)

        self.lm.process_guild_boss_leaderboard(self.gm, week_id, tier_reqs)

        lb = self.lm.get_guild_boss_leaderboard(week_id)
        self.assertEqual(len(lb), 4)

        self.assertEqual(lb[0]["guild_name"], "Alpha")
        self.assertEqual(lb[0]["max_tier"], 3)
        self.assertEqual(lb[0]["damage"], 12000)

        self.assertEqual(lb[1]["guild_name"], "Beta")
        self.assertEqual(lb[1]["max_tier"], 2)
        self.assertEqual(lb[1]["damage"], 6000)

        self.assertEqual(lb[2]["guild_name"], "Gamma")
        self.assertEqual(lb[2]["max_tier"], 2)
        self.assertEqual(lb[2]["damage"], 5500)

        self.assertEqual(lb[3]["guild_name"], "Delta")
        self.assertEqual(lb[3]["max_tier"], 1)
        self.assertEqual(lb[3]["damage"], 2000)

        # Check rewards
        alpha_guild = self.gm.data["guilds"]["Alpha"]
        self.assertIn("Boss Slayer Gold Aura", alpha_guild.get("cosmetic_auras", []))

        beta_guild = self.gm.data["guilds"]["Beta"]
        self.assertIn("Boss Slayer Silver Aura", beta_guild.get("cosmetic_auras", []))

        gamma_guild = self.gm.data["guilds"]["Gamma"]
        self.assertIn("Boss Slayer Bronze Aura", gamma_guild.get("cosmetic_auras", []))

        delta_guild = self.gm.data["guilds"]["Delta"]
        self.assertNotIn("Boss Slayer Bronze Aura", delta_guild.get("cosmetic_auras", []))

if __name__ == '__main__':
    unittest.main()
