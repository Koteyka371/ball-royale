import pytest
from system.guild import GuildManager

def test_guild_hq_customization(tmp_path):
    gm = GuildManager(str(tmp_path / "guilds.json"))
    gm.create_guild("TestGuild", "p1")

    gm.donate_resources("TestGuild", 500)

    hq_details = gm.get_hq_details("TestGuild")
    assert hq_details["arena"] == "basic"
    assert len(hq_details["statues"]) == 0
    assert len(hq_details["banners"]) == 0

    assert gm.unlock_hq_item("TestGuild", "statues", "GoldTrophy", 100) == True
    assert gm.unlock_hq_item("TestGuild", "banners", "RedDragon", 50) == True
    assert gm.unlock_hq_item("TestGuild", "arena", "advanced_training", 200) == True

    # Check resources deducted correctly
    guild = gm.get_guild("TestGuild")
    assert guild["resources"] == 150 # 500 - 100 - 50 - 200

    # Check duplicate prevention
    assert gm.unlock_hq_item("TestGuild", "statues", "GoldTrophy", 100) == False
    assert gm.unlock_hq_item("TestGuild", "arena", "advanced_training", 100) == False

    # Check insufficient funds
    assert gm.unlock_hq_item("TestGuild", "statues", "DiamondTrophy", 200) == False

    hq_details = gm.get_hq_details("TestGuild")
    assert "GoldTrophy" in hq_details["statues"]
    assert "RedDragon" in hq_details["banners"]
    assert hq_details["arena"] == "advanced_training"
