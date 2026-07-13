import pytest
from system.guild import GuildManager
import os
import json

@pytest.fixture
def guild_manager(tmp_path):
    filename = tmp_path / "test_guilds.json"
    return GuildManager(filename=str(filename))

def test_form_alliance(guild_manager):
    guild_manager.create_guild("GuildA", "player1")
    guild_manager.create_guild("GuildB", "player2")

    assert guild_manager.form_alliance("GuildA", "GuildB") == True

    g_a = guild_manager.get_guild("GuildA")
    g_b = guild_manager.get_guild("GuildB")
    assert "GuildB" in g_a["allies"]
    assert "GuildA" in g_b["allies"]

def test_break_alliance(guild_manager):
    guild_manager.create_guild("GuildA", "player1")
    guild_manager.create_guild("GuildB", "player2")
    guild_manager.form_alliance("GuildA", "GuildB")

    assert guild_manager.break_alliance("GuildA", "GuildB") == True

    g_a = guild_manager.get_guild("GuildA")
    g_b = guild_manager.get_guild("GuildB")
    assert "GuildB" not in g_a["allies"]
    assert "GuildA" not in g_b["allies"]

def test_shared_passive_resources(guild_manager):
    guild_manager.create_guild("GuildA", "player1")
    guild_manager.create_guild("GuildB", "player2")
    guild_manager.create_guild("GuildC", "player3")

    guild_manager.form_alliance("GuildA", "GuildB")
    guild_manager.capture_territory("GuildA", "Territory1")

    guild_manager.collect_passive_resources()

    # GuildA owns Territory1, gets 5. GuildB is an ally, gets 2. GuildC gets 0.
    assert guild_manager.get_guild("GuildA")["resources"] == 5
    assert guild_manager.get_guild("GuildB")["resources"] == 2
    assert guild_manager.get_guild("GuildC")["resources"] == 0

def test_alliance_boss_damage_pooling(guild_manager):
    guild_manager.create_guild("GuildA", "player1")
    guild_manager.create_guild("GuildB", "player2")

    guild_manager.form_alliance("GuildA", "GuildB")

    guild_manager.record_boss_damage("GuildA", 500, "week1", tier=1)
    guild_manager.record_boss_damage("GuildB", 600, "week1", tier=1)

    # Required is 1000. Combined is 1100.
    assert guild_manager.check_boss_defeated("GuildA", "week1", 1000, tier=1) == True
    assert guild_manager.check_boss_defeated("GuildB", "week1", 1000, tier=1) == True
    assert guild_manager.check_boss_defeated("GuildA", "week1", 1200, tier=1) == False

    # Player in GuildA can claim it
    assert guild_manager.claim_boss_reward("GuildA", "player1", "week1", 1000, tier=1) == True
    # Can't claim twice
    assert guild_manager.claim_boss_reward("GuildA", "player1", "week1", 1000, tier=1) == False

    # Player in GuildB can claim it too
    assert guild_manager.claim_boss_reward("GuildB", "player2", "week1", 1000, tier=1) == True

    # Verify resources
    assert guild_manager.get_guild("GuildA")["resources"] == 100
    assert guild_manager.get_guild("GuildB")["resources"] == 100

def test_claim_boss_reward_no_own_damage(guild_manager):
    guild_manager.create_guild("GuildA", "player1")
    guild_manager.create_guild("GuildB", "player2")

    guild_manager.form_alliance("GuildA", "GuildB")

    # Only GuildA does damage
    guild_manager.record_boss_damage("GuildA", 1000, "week1", tier=1)

    # Required is 1000. Combined is 1000.
    assert guild_manager.check_boss_defeated("GuildB", "week1", 1000, tier=1) == True

    # Player in GuildB can claim it even though GuildB has 0 damage
    assert guild_manager.claim_boss_reward("GuildB", "player2", "week1", 1000, tier=1) == True
    assert guild_manager.get_guild("GuildB")["resources"] == 100
