import pytest
from system.guild import GuildManager

def test_guild_stronghold(tmp_path):
    gm = GuildManager(str(tmp_path / "guilds.json"))
    gm.create_guild("StrongGuild", "player1")

    # Grant upgrade
    assert gm.grant_stronghold_upgrade("StrongGuild") == True

    guild = gm.get_guild("StrongGuild")
    assert guild.get("stronghold_upgrade_tokens") == 1

    # Apply upgrade
    assert gm.apply_stronghold_upgrade("StrongGuild", "defenses") == True
    assert guild.get("stronghold_upgrade_tokens") == 0

    status = gm.get_stronghold_status("StrongGuild")
    assert status["defenses"] == 1
    assert status["aura_buffs"] == 0

    assert gm.apply_stronghold_upgrade("StrongGuild", "traps") == False # no tokens
