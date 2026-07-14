import pytest
from system.clan import ClanManager
from ai.game_modes import ClanWarMode

class MockBall:
    def __init__(self, team, clan=None, hp=100):
        self.team = team
        self.clan = clan
        self.hp = hp
        self.x = 250
        self.y = 250

class MockWorld:
    pass

def test_clan_territory(tmp_path):
    cm = ClanManager(str(tmp_path / "clans.json"))
    cm.create_clan("ClanA", "p1")
    cm.create_clan("ClanB", "p2")

    assert cm.capture_territory("ClanA", "Arena_1") == True
    assert cm.get_territory_owner("Arena_1") == "ClanA"
    assert "Arena_1" in cm.get_clan_territories("ClanA")

    assert cm.capture_territory("ClanB", "Arena_1") == True
    assert cm.get_territory_owner("Arena_1") == "ClanB"
    assert "Arena_1" not in cm.get_clan_territories("ClanA")

def test_clan_war_mode_bonuses(tmp_path, monkeypatch):
    class MockCM:
        def get_territory_owner(self, t):
            return "ClanA"

    mode = ClanWarMode()

    # We patch inside the setup

    import sys
    sys.modules["system.clan"].ClanManager = MockCM

    b1 = MockBall(1, "ClanA")
    b2 = MockBall(2, "ClanB")
    mode.setup(MockWorld(), [b1, b2])

    # b1 gets bonus
    assert getattr(b1, "speed_multiplier", 1.0) > 1.1
    # b2 does not
    assert getattr(b2, "speed_multiplier", 1.0) == 1.0

    # restore
    sys.modules["system.clan"].ClanManager = ClanManager
