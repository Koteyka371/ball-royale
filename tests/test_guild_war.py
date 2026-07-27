import pytest
from ai.game_modes import GuildWarMode
from ai.action import Action
import math
import sys

# Mock GuildManager
class MockGM:
    def get_hq_defenses(self, guild_name):
        if guild_name == "DefenderGuild":
            return {"turret": 2, "wall": 4, "trap": 1}
        return {"turret": 1}
    def record_siege_defense_broken(self, *args):
        return 1000

# Mock module
import types
mock_system = types.ModuleType("system")
mock_system_guild = types.ModuleType("system.guild")
mock_system_guild.GuildManager = MockGM
sys.modules["system"] = mock_system
sys.modules["system.guild"] = mock_system_guild

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.balls = []
        self.dead_balls = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id, clan="Attacker"):
        self.id = id
        self.clan = clan
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.alive = True
        self.hp = 100
        self.radius = 15.0

def test_guild_war_setup():
    world = MockWorld()

    mode = GuildWarMode("AttackerGuild", "DefenderGuild")

    balls = [MockBall(1)]
    mode.setup(world, balls)

    assert any(getattr(h, "kind", "") == "hq_core" for h in world.arena.hazards)
    turrets = [h for h in world.arena.hazards if getattr(h, "kind", "") == "turret"]
    walls = [h for h in world.arena.hazards if getattr(h, "kind", "") == "bone_wall"]
    traps = [h for h in world.arena.hazards if getattr(h, "kind", "") == "landmine"]

    assert len(turrets) == 2
    assert len(walls) == 4
    assert len(traps) == 1

def test_guild_war_tick():
    world = MockWorld()

    mode = GuildWarMode("AttackerGuild", "DefenderGuild")
    balls = [MockBall(1)]
    balls[0].x = 500
    balls[0].y = 500
    mode.setup(world, balls)

    for _ in range(100):
        mode.tick(world, balls, delta=0.016)

    projectiles = [h for h in world.arena.hazards if getattr(h, "kind", "") == "laser_projectile"]
    assert len(projectiles) > 0

    hq = next((h for h in world.arena.hazards if getattr(h, "kind", "") == "hq_core"), None)
    hq.active = False

    mode.tick(world, balls, delta=0.016)

    assert mode.war_resolved
    assert any(e[0] == "guild_war_victory" for e in world.events)
