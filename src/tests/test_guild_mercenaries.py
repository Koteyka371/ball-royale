import pytest
from system.guild import GuildManager
import os

@pytest.fixture
def guild_manager(tmp_path):
    filename = tmp_path / "test_guilds_mercs.json"
    return GuildManager(filename=str(filename))

def test_hire_mercenary(guild_manager):
    guild_manager.create_guild("Attacker", "p1")
    guild_manager.create_guild("Defender", "p2")

    guild_manager.declare_war("Attacker", "Defender")

    # Give resources
    guild_manager.data["guilds"]["Attacker"]["resources"] = 500

    # Hire mercenary
    assert guild_manager.hire_mercenary("Attacker", "Defender", 100) == True

    mercs = guild_manager.get_hired_mercenaries("Attacker")
    assert len(mercs) == 1
    assert mercs[0]["target"] == "Defender"
    assert "basic" in mercs[0]["traits"]
    assert "veteran" not in mercs[0]["traits"]
    assert mercs[0]["level"] == 1

    # Resources depleted
    assert guild_manager.data["guilds"]["Attacker"]["resources"] == 400

def test_hire_mercenary_levels(guild_manager):
    guild_manager.create_guild("Attacker", "p1")
    guild_manager.create_guild("Defender", "p2")
    guild_manager.declare_war("Attacker", "Defender")

    guild_manager.data["guilds"]["Attacker"]["resources"] = 1000

    # Upgrade to level 5
    for _ in range(4):
        guild_manager.upgrade_guild_level("Attacker", 0)

    assert guild_manager.hire_mercenary("Attacker", "Defender", 100) == True
    mercs = guild_manager.get_hired_mercenaries("Attacker")
    assert len(mercs) == 1
    assert "veteran" in mercs[0]["traits"]
    assert "elite" not in mercs[0]["traits"]
    assert mercs[0]["level"] == 5

    # Upgrade to level 10
    for _ in range(5):
        guild_manager.upgrade_guild_level("Attacker", 0)

    assert guild_manager.hire_mercenary("Attacker", "Defender", 100) == True
    mercs = guild_manager.get_hired_mercenaries("Attacker")
    assert len(mercs) == 2
    assert "elite" in mercs[1]["traits"]
    assert mercs[1]["level"] == 10

def test_hire_mercenary_no_war(guild_manager):
    guild_manager.create_guild("Attacker", "p1")
    guild_manager.create_guild("Defender", "p2")

    guild_manager.data["guilds"]["Attacker"]["resources"] = 500

    # Not at war
    assert guild_manager.hire_mercenary("Attacker", "Defender", 100) == False

    mercs = guild_manager.get_hired_mercenaries("Attacker")
    assert len(mercs) == 0

def test_hire_mercenary_no_resources(guild_manager):
    guild_manager.create_guild("Attacker", "p1")
    guild_manager.create_guild("Defender", "p2")
    guild_manager.declare_war("Attacker", "Defender")

    guild_manager.data["guilds"]["Attacker"]["resources"] = 50

    # Cost is 100, only have 50
    assert guild_manager.hire_mercenary("Attacker", "Defender", 100) == False
