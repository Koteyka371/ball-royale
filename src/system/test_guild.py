import os
import json
import pytest
from system.guild import GuildManager
from system.profile import ProfileManager

@pytest.fixture
def temp_guild_file(tmp_path):
    file_path = tmp_path / "test_guilds.json"
    yield str(file_path)

@pytest.fixture
def temp_profile_file(tmp_path):
    file_path = tmp_path / "test_profile.json"
    yield str(file_path)

def test_create_guild(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    assert gm.create_guild("TestGuild", "player1") == True
    assert gm.create_guild("TestGuild", "player2") == False # Already exists

    guild = gm.get_guild("TestGuild")
    assert guild is not None
    assert "player1" in guild["members"]
    assert guild["resources"] == 0

def test_join_and_leave_guild(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("TestGuild", "player1")

    assert gm.join_guild("TestGuild", "player2") == True
    assert gm.join_guild("NonExistent", "player3") == False

    guild = gm.get_guild("TestGuild")
    assert "player2" in guild["members"]

    assert gm.leave_guild("TestGuild", "player2") == True
    guild = gm.get_guild("TestGuild")
    assert "player2" not in guild["members"]

def test_guild_disbands_when_empty(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("SoloGuild", "player1")
    assert gm.leave_guild("SoloGuild", "player1") == True
    assert gm.get_guild("SoloGuild") is None

def test_donate_and_unlock_buffs(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("BuffGuild", "player1")

    assert gm.donate_resources("BuffGuild", 100) == True
    guild = gm.get_guild("BuffGuild")
    assert guild["resources"] == 100

    assert gm.unlock_buff("BuffGuild", "bonus_hp", 50) == True
    guild = gm.get_guild("BuffGuild")
    assert guild["resources"] == 50
    assert guild["buffs"]["bonus_hp"] == 1

    assert gm.unlock_buff("BuffGuild", "bonus_hp", 100) == False # Not enough resources

def test_gvg_match_recording(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("GuildA", "player1")
    gm.create_guild("GuildB", "player2")

    assert gm.record_gvg_match("GuildA", "GuildB", "GuildA") == True

    assert gm.get_guild("GuildA")["gvg_points"] == 10
    assert gm.get_guild("GuildB")["gvg_points"] == 0

    gm.record_gvg_match("GuildA", "GuildB", "GuildB")
    assert gm.get_guild("GuildA")["gvg_points"] == 5
    assert gm.get_guild("GuildB")["gvg_points"] == 10

def test_profile_guild_integration(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    assert pm.data["guild_name"] == ""

    pm.data["guild_name"] = "MyGuild"
    pm.save()

    pm2 = ProfileManager(temp_profile_file)
    assert pm2.data["guild_name"] == "MyGuild"

    pm2.do_prestige()
    assert pm2.data["guild_name"] == "MyGuild"
