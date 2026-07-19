import pytest
from system.guild import GuildManager
import os

@pytest.fixture
def guild_manager(tmp_path):
    filename = tmp_path / "test_guilds.json"
    return GuildManager(filename=str(filename))

def test_declare_war(guild_manager):
    guild_manager.create_guild("GuildA", "p1")
    guild_manager.create_guild("GuildB", "p2")
    guild_manager.form_alliance("GuildA", "GuildB")

    assert guild_manager.declare_war("GuildA", "GuildB") == True
    g_a = guild_manager.get_guild("GuildA")
    g_b = guild_manager.get_guild("GuildB")

    assert "GuildB" not in g_a.get("allies", [])
    assert "GuildB" in g_a.get("wars", [])
    assert "GuildA" in g_b.get("wars", [])

def test_end_war(guild_manager):
    guild_manager.create_guild("GuildA", "p1")
    guild_manager.create_guild("GuildB", "p2")
    guild_manager.declare_war("GuildA", "GuildB")

    guild_manager.capture_territory("GuildB", "Territory1")
    assert guild_manager.get_territories("GuildB") == ["Territory1"]

    assert guild_manager.end_war("GuildA", "GuildB") == True

    g_a = guild_manager.get_guild("GuildA")
    g_b = guild_manager.get_guild("GuildB")

    assert "GuildB" not in g_a.get("wars", [])
    assert "GuildA" not in g_b.get("wars", [])

    assert guild_manager.get_territories("GuildB") == []
    assert guild_manager.get_territories("GuildA") == ["Territory1"]
    assert "GuildA" in g_b.get("pay_taxes_to", [])

def test_war_taxes(guild_manager):
    guild_manager.create_guild("GuildA", "p1")
    guild_manager.create_guild("GuildB", "p2")

    guild_manager.declare_war("GuildA", "GuildB")
    guild_manager.end_war("GuildA", "GuildB")

    guild_manager.capture_territory("GuildB", "Territory2") # Guild B gets a new territory

    guild_manager.collect_passive_resources()

    g_a = guild_manager.get_guild("GuildA")
    g_b = guild_manager.get_guild("GuildB")

    # Guild B has Territory2, gets 5 base, but 50% taxed -> 2
    # Guild A gets 50% tax from Guild B -> 2 (integer division)

    # Actually wait: B's territory gives 5. 5 * 0.5 = 2.
    # B gets 5 - 2 = 3.
    # A gets 2.
    # Plus A has Territory1 from previous test but since this is a new setup, A has no territories.
    # Let's check exact amounts.

    assert g_a["resources"] == 2
    assert g_b["resources"] == 3
