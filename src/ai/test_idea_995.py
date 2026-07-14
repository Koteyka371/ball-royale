import pytest
from src.ai.game_modes import GAME_MODES
from src.ai.action import Action
import math

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = MockArena()
    def add_event(self, event_type, data):
        self.events.append({'type': event_type, 'data': data})
    def _deal_damage(self, target, attacker):
        target.hp -= getattr(attacker, "damage", 10.0)

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

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

def test_idea_995_tag_team_combo():
    mode = GAME_MODES["tag_team"]
    mode.swap_timer = 9.9  # Almost time to swap
    mode.swap_interval = 10.0

    world = MockWorld()

    # Active tag team player
    b1 = MockEntity(1, 100, 100, "players", tag_team_id=1)
    b1.tag_recent_hit_timer = 1.0  # Has recently hit an enemy

    # Inactive tag team player
    b2 = MockEntity(2, -1000, -1000, "spectator", ball_type="spectator", tag_team_id=1)
    b2.tag_original_ball_type = "player"
    b2.tag_original_team = "players"

    # Enemy nearby
    enemy = MockEntity(3, 150, 150, "enemies")

    balls = [b1, b2, enemy]

    # Tick the mode
    mode.tick(world, balls, 0.2)

    # Assert combo unleashed
    assert any(e["type"] == "tag_combo" for e in world.events)
    # Assert explosion spawned
    assert any(e.get("type") == "visual_effect" and e.get("data", {}).get("type") == "explosion" for e in world.events)
    # Assert enemy took 50 damage
    assert enemy.hp == 50.0

    # Active should become spectator
    assert b1.ball_type == "spectator"

    # Inactive should become player
    assert b2.ball_type == "player"
    assert b2.x == 100
    assert b2.y == 100

def test_idea_995_action_timer_update():
    world = MockWorld()
    action = Action(None, world)

    attacker = MockEntity(1, 100, 100, "players", tag_team_id=1)
    attacker.attack_accuracy = 1.0
    target = MockEntity(2, 120, 120, "enemies")

    # Target not intangible etc.
    action._attempt_damage(attacker, target)

    assert getattr(attacker, "tag_recent_hit_timer", 0.0) == 2.0
