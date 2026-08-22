import pytest
import os
from ai.game_modes import FactionWarMode

class MockProfileManager:
    def __init__(self):
        self.data = {"nemeses": {"nemesis_enemy": {"local_player": 2}}, "unlocked_balls": ["basic"]}
    def save(self): pass
    def is_nemesis(self, k, v):
        return self.data["nemeses"].get(k, {}).get(v, 0) >= 2
    def join_faction(self, f):
        self.data["faction"] = f
    def get_faction(self):
        return self.data.get("faction")

class MockGuildManager:
    def __init__(self):
        self.data = {"guilds": {"MyGuild": {"resources": 100}}}
    def save(self): pass

class MockWorld:
    def __init__(self):
        self.profile_manager = MockProfileManager()
        self.guild_manager = MockGuildManager()
        self.active_guild_name = "MyGuild"

class MockBall:
    def __init__(self, t):
        self.ball_type = t
        self.alive = True
        self.active = True
        self.x = 0
        self.y = 0

def test_faction_war_guild_rewards():
    mode = FactionWarMode()
    world = MockWorld()
    world.profile_manager.join_faction("Light")

    mode.light_points = 5
    mode.dark_points = 0

    # End season
    mode.season_timer = -1.0
    mode.tick(world, [])

    assert mode.season_ended == True
    assert mode.winning_faction == "Light"

    # Check if guild got reward
    assert world.guild_manager.data["guilds"]["MyGuild"]["resources"] == 1100
