import pytest
from unittest.mock import MagicMock

from ai.game_modes import ClanHubMode

class MockClanManager:
    def __init__(self):
        self.data = {
            "clans": {
                "TestClan": {
                    "hub": [
                        {"decoration": "Champion_Trophy", "x": 100, "y": 100},
                        {"decoration": "Speed_Statue", "x": 150, "y": 150}
                    ],
                    "stash": {
                        "gold": 500,
                        "wood": 100
                    }
                }
            }
        }

    def get_hub_buffs(self, clan_name):
        if clan_name == "TestClan":
            return ["Hub_Speed_Boost", "Hub_Health_Regen"]
        return []

class MockProfileManager:
    def __init__(self):
        self.clan_manager = MockClanManager()

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.profile_manager = MockProfileManager()
        self.arena = MockArena()
        self.events = []
        self.time = 0.0
        self.time = 0.0
        self.hub_clan = "TestClan"
        self.balls = []
        self.clan_manager = None

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

class MockBall:
    def __init__(self, ball_id, clan=None):
        self.id = ball_id
        self.clan = clan
        self.base_damage = 10.0
        self.damage = 10.0
        self.invulnerable = False
        self.base_speed = 100.0
        self.speed = 100.0
        self.hp = 50.0
        self.max_hp = 100.0
        self.alive = True
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0

def test_clan_hub_mode_setup():
    world = MockWorld()
    b1 = MockBall(1, "TestClan")
    b2 = MockBall(2, "TestClan")
    balls = [b1, b2]

    mode = ClanHubMode()
    mode.setup(world, balls)

    # Check combat disabled
    assert b1.base_damage == 0.0
    assert b1.damage == 0.0
    assert b1.invulnerable == True

    # Check hazards spawned
    hazards = world.arena.hazards

    # 2 decorations + 2 stash items + 2 NPCs = 6 hazards
    assert len(hazards) == 6

    decorations = [h for h in hazards if h["kind"] == "clan_decoration"]
    assert len(decorations) == 2
    assert decorations[0]["name"] == "Champion_Trophy"

    stash_piles = [h for h in hazards if h["kind"] == "clan_stash_pile"]
    assert len(stash_piles) == 2
    assert stash_piles[0]["item"] == "gold"
    assert stash_piles[0]["amount"] == 500

    npcs = [h for h in hazards if h["kind"] == "clan_npc"]
    assert len(npcs) == 2
    roles = [npc["role"] for npc in npcs]
    assert "stash_master" in roles
    assert "quest_master" in roles

def test_clan_hub_mode_tick_buffs():
    world = MockWorld()
    b1 = MockBall(1, "TestClan")
    world.balls = [b1]

    mode = ClanHubMode()
    mode.hub_clan = "TestClan"
    world.time = 2.0
    mode.tick(world, 0.5)

    # Check buffs applied
    # Base speed should be 100 + (20 * 0.5) = 110
    assert b1.speed == 120.0
    # HP should be 50 + (5 * 0.5) = 52.5
    assert b1.hp == 52.5

def test_clan_hub_mode_tick_npc_interaction():
    world = MockWorld()
    b1 = MockBall(1, "TestClan")
    # Place ball exactly on NPC location
    b1.x = 400.0
    b1.y = 100.0
    world.balls = [b1]

    # Add an NPC to hazards
    world.arena.hazards = [{
        "kind": "clan_npc",
        "role": "stash_master",
        "x": 400.0,
        "y": 100.0,
        "radius": 30.0
    }]

    mode = ClanHubMode()
    mode.hub_clan = "TestClan"

    world.time = 2.0
    mode.tick(world, 0.5)

    # Verify interaction event was added
    assert len(world.events) == 1
    assert world.events[0]["type"] == "npc_interaction"
    assert world.events[0]["data"]["npc"] == "stash_master"
    assert world.events[0]["data"]["player"] == 1
