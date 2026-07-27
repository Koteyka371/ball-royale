import pytest
from ai.game_modes import GuildHQDefenseMode
from system.guild import GuildManager

class MockBall:
    def __init__(self, bid):
        self.id = bid
        self.x = 450
        self.y = 450
        self.hp = 100.0
        self.alive = True
        self.vx = 10.0
        self.vy = 10.0
        self.radius = 15.0

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.events = []
    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_guild_hq_defense_setup_and_tick(tmp_path, monkeypatch):
    import sys

    gm = GuildManager(str(tmp_path / "guilds.json"))
    gm.create_guild("GuildA", "p1")
    gm.build_hq_defense("GuildA", "turret", 0, amount=2)
    gm.build_hq_defense("GuildA", "trap", 0, amount=1)
    gm.build_hq_defense("GuildA", "wall", 0, amount=1)

    monkeypatch.setitem(sys.modules, 'system.guild', type('MockSystemGuild', (), {'GuildManager': lambda: gm}))

    b1 = MockBall("d1")
    b2 = MockBall("a1")
    b2.x = 500
    b2.y = 500

    world = MockWorld([b1, b2])
    mode = GuildHQDefenseMode("GuildA")
    mode.setup(world, [b1, b2])

    assert len(mode.turrets) == 2
    assert len(mode.traps) == 1
    assert len(mode.walls) == 1

    mode._tick(1.0)

    # Attacker is at 500,500 which is <150 from HQ (500,500)
    assert mode.hq_hp == 4950.0 # 5000 - 50*1*1

    # Turret at 500,500 is in range 300, it should shoot and damage b2
    assert b2.hp == 70.0 # 100 - 15
