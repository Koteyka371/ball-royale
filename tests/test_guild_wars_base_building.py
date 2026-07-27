import pytest
import sys
import math
sys.path.append("src")

from ui.guild_wars_base_building import GuildWarsBaseBuilding
from ai.guild_wars_base_building import GuildWarsMode

class MockGuildManager:
    def __init__(self):
        self.data = {
            "guilds": {
                "TestGuild": {
                    "resources": 200,
                    "defenses": []
                }
            }
        }
    def save(self):
        pass

def test_guild_wars_base_building():
    gm = MockGuildManager()
    base_builder = GuildWarsBaseBuilding(gm)

    # Test set guild
    base_builder.set_guild("TestGuild")
    assert base_builder.active_guild == "TestGuild"

    # Test building defense with sufficient resources
    assert base_builder.build_defense("turret", 100, 100) == True
    assert len(base_builder.defenses) == 1
    assert gm.data["guilds"]["TestGuild"]["resources"] == 100

    # Test building defense with insufficient resources (need 100, have 100, build wall for 50, then fail turret)
    assert base_builder.build_defense("wall", 200, 200) == True
    assert gm.data["guilds"]["TestGuild"]["resources"] == 50
    assert base_builder.build_defense("turret", 300, 300) == False

    # Test remove defense
    assert base_builder.remove_defense(0) == True
    assert len(base_builder.defenses) == 1

class MockBall:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.hp = 1000
        self.max_hp = 1000
        self.alive = True
        self.radius = 20

class MockWorld:
    def __init__(self, defenses):
        self.guild_defenses = defenses

def test_guild_wars_mode():
    mode = GuildWarsMode()

    defenses = [
        {"type": "turret", "x": 0, "y": 0, "hp": 500, "team": "defender"},
        {"type": "trap", "x": 100, "y": 100, "hp": 100, "team": "defender"}
    ]
    world = MockWorld(defenses)

    attacker = MockBall(0, 50, "attacker")
    defender = MockBall(10, 10, "defender")
    balls = [attacker, defender]

    mode.setup(world, balls)

    # Initial setup check
    assert len(mode.active_defenses) == 2

    # Tick simulation - turret should fire at attacker
    mode.tick(world, balls, delta=0.1)

    # Attacker took 50 damage
    assert attacker.hp == 950
    # Defender took no damage
    assert defender.hp == 1000

    # Move attacker to trap
    attacker.x = 100
    attacker.y = 100
    mode.tick(world, balls, delta=0.1)

    # Attacker took 200 damage from trap
    assert attacker.hp == 750

    # Trap should be destroyed
    assert len(mode.active_defenses) == 1
