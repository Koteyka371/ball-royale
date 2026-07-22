import pytest
from system.guild import GuildManager
from system.profile import ProfileManager
import os

@pytest.fixture
def guild_manager(tmp_path):
    filename = tmp_path / "test_guilds.json"
    return GuildManager(filename=str(filename))

@pytest.fixture
def profile_manager(tmp_path):
    filename = tmp_path / "test_profile.json"
    pm = ProfileManager(filename=str(filename))
    pm.data["mutator_tokens"] = 10
    pm.save()
    return pm

def test_guild_mutator_token_pooling(guild_manager, profile_manager):
    guild_manager.create_guild("MutatorGuild", "p1")

    # Pool tokens
    assert guild_manager.pool_mutator_tokens("MutatorGuild", 5, profile_manager) == True
    assert profile_manager.data["mutator_tokens"] == 5
    assert guild_manager.get_guild("MutatorGuild")["mutator_token_pool"] == 5

    # Insufficient tokens
    assert guild_manager.pool_mutator_tokens("MutatorGuild", 10, profile_manager) == False
    assert profile_manager.data["mutator_tokens"] == 5

def test_guild_gvg_mutator_voting(guild_manager, profile_manager):
    guild_manager.create_guild("GuildA", "p1")
    guild_manager.create_guild("GuildB", "p2")

    profile_manager.data["mutator_tokens"] = 20

    guild_manager.pool_mutator_tokens("GuildA", 10, profile_manager)
    guild_manager.pool_mutator_tokens("GuildB", 10, profile_manager)

    # Cast votes
    assert guild_manager.cast_gvg_mutator_vote("GuildA", "double_damage", 6) == True
    assert guild_manager.cast_gvg_mutator_vote("GuildB", "low_gravity", 4) == True

    assert guild_manager.get_guild("GuildA")["mutator_token_pool"] == 4

    # Get match mutator
    winning = guild_manager.get_gvg_match_mutator("GuildA", "GuildB")
    assert winning == "double_damage" # 6 tokens > 4 tokens

    # Add more votes to B
    guild_manager.cast_gvg_mutator_vote("GuildB", "low_gravity", 3)
    winning = guild_manager.get_gvg_match_mutator("GuildA", "GuildB")
    assert winning == "low_gravity" # 7 tokens > 6 tokens
