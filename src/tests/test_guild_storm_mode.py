import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.game_modes import GuildStormMode

class MockBall:
    def __init__(self, x, y, player_id):
        self.x = x
        self.y = y
        self.player_id = player_id
        self.hp = 100.0
        self.speed = 100.0
        self.damage = 10.0
        self.time_alive = 0.0

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_guild_storm_mechanics(monkeypatch):
    class DummyGuildManager:
        def __init__(self):
            pass
        def get_guild(self, name):
            if name == "Stormers":
                return {"members": ["p1", "p2"], "resources": 1000}
            return None
        def save(self):
            pass

    import sys
    sys.modules['system.guild'] = type('dummy_guild', (), {'GuildManager': DummyGuildManager})

    mode = GuildStormMode(guild_name="Stormers", cost=500)
    world = MockWorld()

    b1 = MockBall(0, 0, "p1") # member
    b2 = MockBall(0, 0, "p3") # non-member
    balls = [b1, b2]

    mode.setup(world, balls)

    assert mode.storm_active is True
    assert len(world.events) > 0

    # Check tick buffs
    mode.tick(world, balls, delta=1.0)

    # Member buffed
    assert b1.speed == b1.base_speed * 1.5
    assert b1.damage == b1.base_damage * 1.5
    assert b1.hp == 100.0

    # Non-member damaged
    assert b2.speed == b2.base_speed
    assert b2.damage == b2.base_damage
    assert b2.hp == 95.0

    # Fast forward to end of storm
    mode.tick(world, balls, delta=30.0)

    assert mode.storm_active is False
    assert b1.speed == b1.base_speed
    assert b1.damage == b1.base_damage
