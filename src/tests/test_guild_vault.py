import pytest
from system.guild import GuildManager

def test_vault_investment(tmp_path):
    manager = GuildManager(filename=str(tmp_path / "guilds.json"))
    manager.create_guild("VaultGuild", "player1")
    guild = manager.data["guilds"]["VaultGuild"]
    guild["resources"] = 1000
    guild["level"] = 1
    manager.save()

    # Invest
    assert manager.invest_in_vault("VaultGuild", 500, 3, "2023-01-01") == True
    assert guild["resources"] == 500
    assert guild["vault_investment"]["amount"] == 500
    assert guild["vault_investment"]["days_remaining"] == 3

    # Cannot invest again while active
    assert manager.invest_in_vault("VaultGuild", 100, 2, "2023-01-01") == False

    # Steal from vault
    manager.create_guild("Attacker", "player2")
    manager.data["guilds"]["Attacker"]["resources"] = 0
    manager.save()

    stolen = manager.steal_from_vault("Attacker", "VaultGuild", 100)
    assert stolen == 100
    assert guild["vault_investment"]["amount"] == 400
    assert manager.data["guilds"]["Attacker"]["resources"] == 100

    # Process days
    manager.process_daily_events("2023-01-02")
    assert guild["vault_investment"]["days_remaining"] == 2
    manager.process_daily_events("2023-01-03")
    assert guild["vault_investment"]["days_remaining"] == 1

    resources_before_payout = guild.get("resources", 0)

    # Temporarily remove trigger_daily_mini_tournament for this test day so we can test exactly
    original_trigger = manager.trigger_daily_mini_tournament
    manager.trigger_daily_mini_tournament = lambda: None

    manager.process_daily_events("2023-01-04")

    # Vault opens: 400 amount. Base yield for level 1: 10% + 1% = 11%
    # 400 * 1.11 = 444
    assert guild["vault_investment"]["amount"] == 0
    assert guild["resources"] == resources_before_payout + 444

    # Test with vault_yield perk
    guild["resources"] = 1000
    guild["perks"] = ["vault_yield"]
    manager.save()
    assert manager.invest_in_vault("VaultGuild", 1000, 1, "2023-01-05") == True

    resources_before_payout2 = guild.get("resources", 0)
    manager.process_daily_events("2023-01-06")

    # Yield = 10% + 1% + 10% = 21%
    # 1000 * 1.21 = 1210
    assert guild["vault_investment"]["amount"] == 0
    assert guild["resources"] == resources_before_payout2 + 1210

    manager.trigger_daily_mini_tournament = original_trigger
