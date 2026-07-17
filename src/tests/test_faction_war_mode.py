import pytest
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

class MockWorld:
    def __init__(self):
        self.profile_manager = MockProfileManager()

class MockBall:
    def __init__(self, t):
        self.ball_type = t
        self.alive = True

def test_faction_war_nemesis_kill():
    mode = FactionWarMode()
    world = MockWorld()
    world.profile_manager.join_faction("Light")

    # local_player (Light) kills nemesis_enemy
    killer = MockBall("local_player")
    victim = MockBall("nemesis_enemy")

    assert world.profile_manager.is_nemesis(victim.ball_type, killer.ball_type) == True

    mode.on_ball_died(world, victim, killer)

    assert mode.light_points == 1
    assert mode.dark_points == 0

    # Trigger season end
    mode.season_timer = -1.0
    mode.tick(world, [killer], 0.1)

    assert mode.season_ended == True
    assert mode.winning_faction == "Light"
    assert "light_champion" in world.profile_manager.data.get("unlocked_balls", [])

def test_faction_war_dark_win():
    mode = FactionWarMode()
    world = MockWorld()
    world.profile_manager.join_faction("Light")

    mode.dark_points = 5
    mode.light_points = 2

    mode.season_timer = -1.0
    mode.tick(world, [], 0.1)

    assert mode.season_ended == True
    assert mode.winning_faction == "Dark"
    assert "dark_champion" not in world.profile_manager.data.get("unlocked_balls", [])
