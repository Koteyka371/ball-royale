import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from system.guild import GuildManager
import tempfile
import json

def test_guild_boss_tier():
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        json.dump({"guilds": {}, "territories": {}}, f)
        temp_file = f.name

    try:
        gm = GuildManager(temp_file)
        gm.create_guild("TestGuild", "player1")

        # Record tier 1
        gm.record_boss_damage("TestGuild", 500, "week_1", tier=1)

        # Record tier 2
        gm.record_boss_damage("TestGuild", 1000, "week_1", tier=2)

        # Check
        assert gm.check_boss_defeated("TestGuild", "week_1", 500, tier=1)
        assert gm.check_boss_defeated("TestGuild", "week_1", 1000, tier=2)
        assert not gm.check_boss_defeated("TestGuild", "week_1", 2000, tier=2)

        # Claim tier 1
        assert gm.claim_boss_reward("TestGuild", "player1", "week_1", 500, tier=1)
        assert gm.data["guilds"]["TestGuild"]["resources"] == 100

        # Claim tier 2
        assert gm.claim_boss_reward("TestGuild", "player1", "week_1", 1000, tier=2)
        assert gm.data["guilds"]["TestGuild"]["resources"] == 300 # 100 + 200

    finally:
        os.remove(temp_file)
