import unittest
import os
import json
from unittest.mock import patch
from ui.main_menu import MainMenu
from ui.clan_emissary_quests import ClanEmissary
from system.profile import ProfileManager
from system.leaderboard import LeaderboardManager

class TestClanEmissary(unittest.TestCase):
    def setUp(self):
        self.profile_file = "test_profile_emissary.json"
        if os.path.exists(self.profile_file):
            os.remove(self.profile_file)
        self.profile_manager = ProfileManager(self.profile_file)
        self.clan_emissary = ClanEmissary(self.profile_manager)

    def tearDown(self):
        if os.path.exists(self.profile_file):
            os.remove(self.profile_file)

    def test_complete_quest(self):
        self.assertEqual(self.profile_manager.data.get("emissary_tokens", 0), 0)
        self.assertTrue(self.clan_emissary.complete_quest("q1"))
        self.assertEqual(self.profile_manager.data.get("emissary_tokens", 0), 10)
        self.assertIn("q1", self.profile_manager.data.get("completed_clan_quests", []))

        # Test cannot complete twice
        self.assertFalse(self.clan_emissary.complete_quest("q1"))
        self.assertEqual(self.profile_manager.data.get("emissary_tokens", 0), 10)

    def test_buy_item(self):
        self.profile_manager.data["emissary_tokens"] = 10
        self.profile_manager.save()

        self.assertTrue(self.clan_emissary.buy_item("item1"))
        self.assertEqual(self.profile_manager.data.get("emissary_tokens", 0), 0)
        self.assertIn("item1", self.profile_manager.data.get("clan_inventory", []))

        # Test insufficient tokens
        self.assertFalse(self.clan_emissary.buy_item("item1"))

class TestMainMenuEmissary(unittest.TestCase):
    @patch('system.profile.ProfileManager.__init__', return_value=None)
    @patch('system.leaderboard.LeaderboardManager.__init__', return_value=None)
    @patch('ui.nemesis_screen.nemesis_screen.NemesisScreen.__init__', return_value=None)
    @patch('ui.guild_emblem_editor.guild_emblem_editor.GuildEmblemEditor.__init__', return_value=None)
    @patch('ui.prestige_shop.prestige_shop.PrestigeShop.__init__', return_value=None)
    @patch('system.leaderboard.LeaderboardManager.get_theme', return_value="Genesis")
    def setUp(self, mock_theme, mock_ps, mock_ge, mock_ns, mock_lb, mock_pm):
        # We manually patch the object after it creates it because LeaderboardManager doesn't define data as class variable
        with patch('ui.main_menu.LeaderboardManager') as MockLM, \
             patch('ui.main_menu.ProfileManager') as MockPM:

             mock_lm_inst = MockLM.return_value
             mock_lm_inst.data = {"current_season": 1}
             mock_lm_inst.get_theme.return_value = "Genesis"

             mock_pm_inst = MockPM.return_value
             mock_pm_inst.data = {}

             self.main_menu = MainMenu()
             # rebind the properties manually because they refer to the original mock_pm_inst
             self.main_menu.profile_manager = mock_pm_inst
             self.main_menu.leaderboard_manager = mock_lm_inst
             self.main_menu.clan_emissary = ClanEmissary(mock_pm_inst)

    def test_open_clan_emissary(self):
        self.assertEqual(self.main_menu.active_screen, "main")
        res = self.main_menu.open_clan_emissary()
        self.assertEqual(self.main_menu.active_screen, "clan_emissary")
        self.assertIn("quests", res)
        self.assertIn("shop_items", res)

    def test_process_input_emissary(self):
        self.main_menu.open_clan_emissary()
        self.assertTrue(self.main_menu.process_input("complete_quest", "q1"))
        self.assertEqual(self.main_menu.profile_manager.data.get("emissary_tokens"), 10)

        self.assertTrue(self.main_menu.process_input("buy_item", "item1"))
        self.assertEqual(self.main_menu.profile_manager.data.get("emissary_tokens"), 0)
        self.assertIn("item1", self.main_menu.profile_manager.data.get("clan_inventory", []))

        self.assertTrue(self.main_menu.process_input("back"))
        self.assertEqual(self.main_menu.active_screen, "main")
