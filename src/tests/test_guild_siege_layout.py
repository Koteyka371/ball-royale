from system.guild import GuildManager
import pytest

def test_guild_siege_layout(tmp_path):
    gm = GuildManager(str(tmp_path / "guilds.json"))
    gm.create_guild("SiegeGuild", "p1")
    gm.data["guilds"]["SiegeGuild"]["resources"] = 5000

    assert gm.arrange_siege_defense("SiegeGuild", "trap_spike", 2, 3) == True
    assert gm.arrange_siege_defense("SiegeGuild", "trap_fire", 2, 4) == True
    assert gm.arrange_siege_defense("SiegeGuild", "turret_laser", 5, 5) == True

    layout = gm.get_siege_layout("SiegeGuild")
    assert layout.get("2,3") == "trap_spike"
    assert layout.get("2,4") == "trap_fire"
    assert layout.get("5,5") == "turret_laser"

    synergy = gm.calculate_siege_synergy("SiegeGuild")
    # Spike and fire adjacent -> 10% bonus
    assert synergy > 0
