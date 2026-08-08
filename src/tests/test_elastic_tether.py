from unittest.mock import MagicMock
from ai.action import Action
import pytest

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.boosters = []
        self.projectiles = []

class MockBall:
    def __init__(self, id, team, ball_type="player"):
        self.id = id
        self.team = team
        self.type = ball_type
        self.x = 500.0
        self.y = 500.0
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.skill_timer = 0.0
        self.SKILL_COOLDOWN = 5.0
        self.skill = "elastic_tether"
        self.active_skill = "elastic_tether"
        self.SKILL = "elastic_tether"
        self.active_skill_name = "elastic_tether"
        self.radius = 20.0
        self.elastic_tether_timer = 0.0
        self.elastic_tether_target = None
        self.stun_timer = 0.0

def test_elastic_tether_hooks_enemy_and_pulls_together():
    world = MockWorld()
    b1 = MockBall(1, "red")
    b2 = MockBall(2, "blue")
    b2.x = 600.0
    b2.y = 500.0
    world.balls = [b1, b2]

    action = Action(b1, world)

    # Trigger skill execution manually by modifying internal states as it's evaluated in loop
    b1.skill = "elastic_tether"
    action.execute("use_skill", 1.0)

    assert b1.elastic_tether_timer > 0.0
    assert b1.elastic_tether_target == b2

    # Process idle logic to verify pull
    action.execute("idle", 1.0)

    assert b1.vx > 0.0 or b2.vx < 0.0
    assert b2.vx < 0.0

def test_elastic_tether_stuns_on_collision():
    world = MockWorld()
    b1 = MockBall(1, "red")
    b2 = MockBall(2, "blue")
    # Put them very close to trigger collision stun immediately
    b2.x = 510.0
    b2.y = 500.0
    world.balls = [b1, b2]

    action = Action(b1, world)

    b1.skill = "elastic_tether"
    action.execute("use_skill", 1.0)

    # Process idle logic
    action.execute("idle", 1.0)

    assert b1.stun_timer > 0.0
    assert b2.stun_timer > 0.0
    assert b1.elastic_tether_timer == 0.0 # Tether breaks
