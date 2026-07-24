import pytest
import os
import json
from ui.main_menu import MainMenu
import system.profile
import system.leaderboard
import system.guild
from ui.guild_emblem_editor.guild_emblem_editor import GuildEmblemEditor

def test_main_menu_emblem_editor():
    class DummyProfileManager:
        def __init__(self):
            self.data = {"username": "player1"}

    class DummyGuildManager:
        def __init__(self):
            self.data = {
                "guilds": {
                    "TestGuild": {
                        "members": ["player1"],
                        "emblem": {"shape": "circle", "color": "white", "symbol": "none"},
                        "unlocked_emblem_parts": {
                            "shapes": ["circle", "shield"],
                            "colors": ["white", "red"],
                            "symbols": ["none", "sword"]
                        }
                    }
                }
            }
        def get_guild(self, guild_name):
            return self.data["guilds"].get(guild_name)

        def update_emblem(self, guild_name, shape, color, symbol):
            if guild_name in self.data["guilds"]:
                self.data["guilds"][guild_name]["emblem"] = {"shape": shape, "color": color, "symbol": symbol}
                return True
            return False

    menu = MainMenu()
    menu.profile_manager = DummyProfileManager()
    menu.guild_manager = DummyGuildManager()
    menu.guild_emblem_editor = GuildEmblemEditor(menu.profile_manager)
    menu.guild_emblem_editor.guild_manager = menu.guild_manager

    res = menu.open_guild_emblem_editor()
    assert res["guild_name"] == "TestGuild"
    assert menu.active_screen == "guild_emblem_editor"

    assert menu.guild_emblem_editor.current_shape == "circle"

    menu.process_input("next_shape")
    assert menu.guild_emblem_editor.current_shape == "shield"

    menu.process_input("next_color")
    assert menu.guild_emblem_editor.current_color == "red"

    menu.process_input("next_symbol")
    assert menu.guild_emblem_editor.current_symbol == "sword"

    assert menu.process_input("save") == True

    menu.process_input("back")
    assert menu.active_screen == "main"
