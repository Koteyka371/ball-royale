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
        self.id = 1

    def get_clan(self):
        return self.clan

class MockHazardObj:
    def __init__(self):
        self.id = 2
        self.kind = "fire_zone"
        self.team = None
        self.owner_team = None

class MockArena:
    def __init__(self):
        self.hazards = [MockHazardObj()]

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_clan_war_hazard_friendly_obj(tmp_path, monkeypatch):
    class MockCM:
        def get_territory_owner(self, t):
            return "ClanA"

        def capture_territory(self, clan, t):
            return True

    mode = ClanWarMode()

    import sys
    sys.modules["system.clan"].ClanManager = MockCM

    b1 = MockBall(1, "ClanA")
    b2 = MockBall(2, "ClanB")
    world = MockWorld()
    mode.setup(world, [b1, b2])

    mode.tick(world, [b1, b2], 0.1)

    assert world.arena.hazards[0].team == 1
    assert world.arena.hazards[0].owner_team == 1

    sys.modules["system.clan"].ClanManager = ClanManager
