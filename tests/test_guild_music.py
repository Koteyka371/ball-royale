import pytest
from src.system.guild import GuildManager

def test_ambient_music_unlock_and_set(tmp_path):
    gm = GuildManager(str(tmp_path / "guilds.json"))
    gm.create_guild("Music Guild", "DJ")

    # Give guild resources and guild_xp
    guild = gm.get_guild("Music Guild")

    # Actually just set directly for test
    gm.data["guilds"]["Music Guild"]["guild_xp"] = 1000
    gm.save()

    # Try unlocking ambient_music using guild_xp
    success = gm.unlock_hq_feature("Music Guild", "ambient_music", "track_jazz_1", 200, required_level=1, currency="guild_xp")
    assert success

    # Verify in hq status
    hq = gm.get_hq_status("Music Guild")
    assert "track_jazz_1" in hq["ambient_music"]
    assert hq["active_ambient_music"] is None

    # Set active track
    success = gm.set_hq_ambient_music("Music Guild", "track_jazz_1")
    assert success

    hq2 = gm.get_hq_status("Music Guild")
    assert hq2["active_ambient_music"] == "track_jazz_1"

    # Try setting unknown track
    success = gm.set_hq_ambient_music("Music Guild", "track_metal_1")
    assert not success
