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

def test_hq_customization(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("HQGuild", "player1")

    # Needs resources
    assert gm.unlock_hq_feature("HQGuild", "statues", "golden_ball", 500) == False

    gm.donate_resources("HQGuild", 1000)

    # Unlock statue
    assert gm.unlock_hq_feature("HQGuild", "statues", "golden_ball", 500) == True
    # Can't unlock same statue
    assert gm.unlock_hq_feature("HQGuild", "statues", "golden_ball", 500) == False

    # Unlock training arena
    assert gm.unlock_hq_feature("HQGuild", "training_arena", "", 500) == True
    assert gm.unlock_hq_feature("HQGuild", "training_arena", "", 500) == False # Already unlocked

    hq_status = gm.get_hq_status("HQGuild")
    assert hq_status is not None
    assert "golden_ball" in hq_status["statues"]
    assert hq_status["training_arena_unlocked"] == True

def test_guild_perk_progression(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("PerkGuild", "p1")
    gm.create_guild("OtherGuild", "p2")

    # Give some XP via GvG
    gm.record_gvg_match("PerkGuild", "OtherGuild", "PerkGuild") # PerkGuild +50 XP
    gm.record_gvg_match("PerkGuild", "OtherGuild", "PerkGuild") # PerkGuild +50 XP, total 100

    guild = gm.get_guild("PerkGuild")
    assert guild["guild_xp"] == 100

    # Try unlocking a perk
    assert gm.unlock_perk("PerkGuild", "hp_5_percent", 50) == True
    assert guild["guild_xp"] == 50
    assert "hp_5_percent" in gm.get_guild_perks("PerkGuild")

    # Try unlocking same perk again
    assert gm.unlock_perk("PerkGuild", "hp_5_percent", 10) == False

    # Try unlocking with insufficient XP
    assert gm.unlock_perk("PerkGuild", "hp_10_percent", 100) == False

    # Try unlocking with missing dependency
    # Let's say hp_10_percent requires hp_5_percent, but damage_10_percent requires damage_5_percent
    assert gm.unlock_perk("PerkGuild", "damage_10_percent", 50, required_perk="damage_5_percent") == False

    # Get more XP
    gm.record_gvg_match("PerkGuild", "OtherGuild", "PerkGuild") # +50 XP, total 100
    assert gm.unlock_perk("PerkGuild", "hp_10_percent", 100, required_perk="hp_5_percent") == True
    assert "hp_10_percent" in gm.get_guild_perks("PerkGuild")

def test_place_and_get_bounties(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("BountyHunters", "player1")
    gm.create_guild("TargetGuild", "player2")

    # Test getting bounties on empty list
    assert gm.get_active_bounties("BountyHunters") == []

    # Needs resources to place bounty
    assert gm.place_bounty("BountyHunters", "TargetGuild", 500) == False

    # Add resources
    gm.donate_resources("BountyHunters", 1000)

    # Place bounty successfully
    assert gm.place_bounty("BountyHunters", "TargetGuild", 500) == True

    # Check resources deducted
    guild = gm.get_guild("BountyHunters")
    assert guild["resources"] == 500

    # Check active bounties
    assert "TargetGuild" in gm.get_active_bounties("BountyHunters")

    # Place bounty again should fail (already exists)
    assert gm.place_bounty("BountyHunters", "TargetGuild", 500) == False
    assert guild["resources"] == 500
