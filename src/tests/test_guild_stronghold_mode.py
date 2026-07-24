import pytest
from ai.game_modes import GuildVsGuildMode
from system.guild import GuildManager
import os

class MockBall:
    def __init__(self, bid, hp=100):
        self.id = bid
        self.hp = hp
        self.x = 250
        self.y = 250
        self.alive = True
        self.vx = 0
        self.vy = 0

class MockWorld:
    def __init__(self, balls):
        self.balls = balls

def test_gvg_mode_stronghold_buff(tmp_path, monkeypatch):
    gm = GuildManager(str(tmp_path / "guilds.json"))
    gm.create_guild("GuildA", "p1")
    gm.create_guild("GuildB", "p2")

    gm.grant_stronghold_upgrade("GuildA")
    gm.apply_stronghold_upgrade("GuildA", "aura_buffs")

    gm.capture_territory("GuildA", "TerritoryX") # GuildA owns a territory

    def mock_get_territory(self, gn):
        if gn == "GuildA":
            return ["TerritoryX"]
        return []
    def mock_get_status(self, gn):
        if gn == "GuildA":
            return {"defenses": 0, "traps": 0, "aura_buffs": 1}
        return {"defenses": 0, "traps": 0, "aura_buffs": 0}

    # apply monkeypatch
    monkeypatch.setattr(GuildManager, "get_territories", mock_get_territory)
    monkeypatch.setattr(GuildManager, "get_stronghold_status", mock_get_status)

    import sys
    sys.modules["system.guild"].GuildManager = lambda: gm

    b1 = MockBall("A1")
    b2 = MockBall("B1")
    world = MockWorld([b1, b2])

    mode = GuildVsGuildMode()
    mode.setup(world, [b1, b2])

    # Verify setup applied the buff to A1 but not B1
    mode._tick(0.1)

    assert getattr(b1, "stronghold_aura", False) == True
    assert getattr(b2, "stronghold_aura", False) == False

    # Restore
    sys.modules["system.guild"].GuildManager = GuildManager
