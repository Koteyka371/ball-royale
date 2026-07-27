import pytest
from ai.game_modes import GAME_MODES

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, event_type, data):
        self.events.append({'type': event_type, 'data': data})
    def _deal_damage(self, target, attacker):
        target.hp -= getattr(attacker, "damage", 10.0)

class MockEntity:
    def __init__(self, id, x, y, team, ball_type="player", tag_team_id=None):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.tag_team_id = tag_team_id
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.damage = 10.0
        self.traits = []

def test_idea_1585_ultra_ball():
    mode = GAME_MODES["tag_team"]
    mode.swap_timer = 9.9  # Almost time to swap
    mode.swap_interval = 10.0

    world = MockWorld()

    # Active tag team player
    b1 = MockEntity(1, 100, 100, "players", tag_team_id=1)
    b1.tag_recent_hit_timer = 1.0  # Has recently hit an enemy
    b1.tag_combo_chain = 2 # 2 previous chains
    b1.traits = ["fire"]
    b1.tag_original_traits = ["fire"]
    b1.tag_original_ball_type = "player"
    b1.tag_original_team = "players"

    # Inactive tag team player
    b2 = MockEntity(2, -1000, -1000, "spectator", ball_type="spectator", tag_team_id=1)
    b2.traits = ["water"]
    b2.tag_original_traits = ["water"]
    b2.tag_original_ball_type = "player"
    b2.tag_original_team = "players"

    balls = [b1, b2]

    # Tick the mode - should swap and hit combo 3 -> ultra ball
    mode.tick(world, balls, 0.2)

    # b1 became inactive (spectator), b2 became active (player)
    assert b2.ball_type == "player"
    assert b1.ball_type == "spectator"

    # Because chain reached 3, b2 should have ultra ball properties
    assert getattr(b2, "tag_combo_chain", 0) == 0
    assert getattr(b2, "ultra_ball_timer", 0.0) == 10.0
    # Traits merged?
    assert "fire" in b2.traits
    assert "water" in b2.traits

    assert any(e["type"] == "ultra_ball" for e in world.events)

    # Now tick to decay ultra ball timer
    mode.tick(world, balls, 10.0)
    assert b2.ultra_ball_timer == 0.0
    # Traits should reset to original
    assert "fire" not in b2.traits
    assert "water" in b2.traits

    # Check broken combo
    b2.tag_recent_hit_timer = 0.0
    mode.swap_timer = 9.9
    mode.tick(world, balls, 0.2)
    # Swaps back to b1
    assert getattr(b1, "tag_combo_chain", 0) == 0
