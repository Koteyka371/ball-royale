import pytest
from ai.game_modes import GAME_MODES
from ai.action import Action
import math

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = MockArena()
        self.boosters = []
    def add_event(self, event_type, data):
        self.events.append({'type': event_type, 'data': data})
    def _deal_damage(self, target, attacker):
        target.hp -= getattr(attacker, "damage", 10.0)

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

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

def test_idea_1586_tag_assist():
    mode = GAME_MODES["tag_team"]

    world = MockWorld()

    # Active tag team player
    b1 = MockEntity(1, 100, 100, "players", tag_team_id=1)

    # Inactive tag team player
    b2 = MockEntity(2, -1000, -1000, "spectator", ball_type="spectator", tag_team_id=1)
    b2.tag_original_ball_type = "player"
    b2.tag_original_team = "players"
    b2.tag_assist_timer = 0.1 # Ready to drop

    balls = [b1, b2]

    # Tick the mode
    mode.tick(world, balls, 0.2)

    # Check if a booster or trap was dropped
    dropped = False
    if len(world.boosters) > 0:
        dropped = True
        b = world.boosters[0]
        assert abs(b["x"] - b1.x) <= 100
        assert abs(b["y"] - b1.y) <= 100
        assert b["kind"] in ["speed", "health", "shield"]
    elif len(world.arena.hazards) > 0:
        dropped = True
        h = world.arena.hazards[0]
        assert abs(h.x - b1.x) <= 100
        assert abs(h.y - b1.y) <= 100
        assert getattr(h, "kind", "") == "trap"

    assert dropped
    assert any(e["type"] == "tag_assist" for e in world.events)

    # Assert timer was reset
    assert b2.tag_assist_timer > 3.0
