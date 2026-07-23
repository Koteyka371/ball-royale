import pytest
import os
import json
from system.profile import ProfileManager
from system.guild import GuildManager
from ui.guild_emblem_editor.guild_emblem_editor import GuildEmblemEditor

@pytest.fixture
def temp_files(tmp_path):
    profile_file = tmp_path / "test_profile.json"
    guild_file = tmp_path / "test_guilds.json"

    with open(profile_file, "w") as f:
        json.dump({"username": "player1"}, f)

    with open(guild_file, "w") as f:
        json.dump({
            "guilds": {
                "TestGuild": {
                    "members": ["player1", "player2"],
                    "emblem": {"shape": "circle", "color": "white", "symbol": "none"},
                    "unlocked_emblem_parts": {
                        "shapes": ["circle", "shield"],
                        "colors": ["white", "red"],
                        "symbols": ["none", "sword"]
                    }
                }
            }
        }, f)

    return str(profile_file), str(guild_file)

def test_guild_emblem_editor_init(temp_files):
    profile_file, guild_file = temp_files
    pm = ProfileManager(profile_file)
    editor = GuildEmblemEditor(pm)
    editor.guild_manager = GuildManager(guild_file)

    assert editor.current_shape == "circle"
    assert editor.current_color == "white"
    assert editor.current_symbol == "none"

def test_guild_emblem_editor_refresh(temp_files):
    profile_file, guild_file = temp_files
    pm = ProfileManager(profile_file)
    editor = GuildEmblemEditor(pm)
    editor.guild_manager = GuildManager(guild_file)

    res = editor.refresh_ui()
    assert res["guild_name"] == "TestGuild"
    assert res["current_emblem"]["shape"] == "circle"

def test_guild_emblem_editor_save(temp_files):
    profile_file, guild_file = temp_files
    pm = ProfileManager(profile_file)
    editor = GuildEmblemEditor(pm)
    editor.guild_manager = GuildManager(guild_file)

    editor.refresh_ui()

    # Valid parts
    editor.current_shape = "shield"
    editor.current_color = "red"
    editor.current_symbol = "sword"

    assert editor.save_emblem() == True

    # Invalid parts
    editor.current_shape = "hexagon"
    assert editor.save_emblem() == False
