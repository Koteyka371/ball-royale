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

def test_guild_chat(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("ChatGuild", "player1")
    assert gm.send_chat_message("ChatGuild", "player1", "Hello World!") == True
    history = gm.get_chat_history("ChatGuild")
    assert len(history) == 1
    assert history[0]["sender"] == "player1"
    assert history[0]["message"] == "Hello World!"

def test_guild_vault(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("VaultGuild", "player1")
    assert gm.deposit_item("VaultGuild", "sword") == True
    guild = gm.get_guild("VaultGuild")
    assert "sword" in guild["vault"]
    assert gm.withdraw_item("VaultGuild", "shield") == False
    assert gm.withdraw_item("VaultGuild", "sword") == True
    guild = gm.get_guild("VaultGuild")
    assert "sword" not in guild["vault"]

def test_guild_territories(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("Conquerors", "player1")
    assert gm.capture_territory("Conquerors", "Castle") == True
    territories = gm.get_territories("Conquerors")
    assert "Castle" in territories
    assert gm.get_territories("NoGuild") == []

    # test passive resources
    guild = gm.get_guild("Conquerors")
    initial_resources = guild["resources"]
    gm.collect_passive_resources()
    guild = gm.get_guild("Conquerors")
    assert guild["resources"] == initial_resources + 5

def test_guild_leaderboard(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("Guild1", "p1")
    gm.create_guild("Guild2", "p2")
    gm.record_gvg_match("Guild1", "Guild2", "Guild2") # Guild2 wins, gets 10 points

    leaderboard = gm.get_guild_leaderboard()
    assert leaderboard[0]["name"] == "Guild2"
    assert leaderboard[0]["gvg_points"] == 10
    assert leaderboard[1]["name"] == "Guild1"
    assert leaderboard[1]["gvg_points"] == 0

def test_boss_progress(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("BossKillers", "player1")

    week_id = "week_1"
    required_damage = 1000.0

    # Check defeated before damage
    assert not gm.check_boss_defeated("BossKillers", week_id, required_damage)

    # Deal damage
    assert gm.record_boss_damage("BossKillers", 400.0, week_id)
    assert not gm.check_boss_defeated("BossKillers", week_id, required_damage)

    assert gm.record_boss_damage("BossKillers", 700.0, week_id)
    assert gm.check_boss_defeated("BossKillers", week_id, required_damage)

    # Claim rewards
    assert gm.claim_boss_reward("BossKillers", "player1", week_id, required_damage)
    # Should not be able to claim twice
    assert not gm.claim_boss_reward("BossKillers", "player1", week_id, required_damage)
    # Different player can claim
    assert gm.claim_boss_reward("BossKillers", "player2", week_id, required_damage)
