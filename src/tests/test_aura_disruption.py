import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []

class MockBall:
    def __init__(self, id, x, y, team, skill="aura_disruption"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.skill = skill
        self.skill_timer = 0.0
        self.skill_cooldown = 8.0
        self.silence_timer = 0.0
        self.radius = 10.0
        self.alive = True
        self.ball_type = "base"
        self.hp = 100.0

def test_aura_disruption_skill():
    ball = MockBall(1, 0, 0, "team_A")
    enemy = MockBall(2, 50, 0, "team_B")

    world = MockWorld()
    world.balls.extend([ball, enemy])
    action = Action(ball, world)

    # 1. Trigger skill to create thrown hazard
    action._use_skill()

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "thrown_aura_disrupter"
    assert hazard.owner_id == ball.id

    # Check that initial timer is duration 1.5
    assert hazard.duration == 1.5

    # Let duration pass so it detonates
    hazard.duration = 0.001
    action.execute("idle", 0.016)

    # The hazard should be removed
    assert len(world.arena.hazards) == 0

    # The enemy within radius (150) should have aura_disruption_timer set to 10
    assert getattr(enemy, "aura_disruption_timer", 0.0) == 10.0

    # Visual event is added
    assert any(e.get("type") == "visual_effect" and e.get("data", {}).get("type") == "aura_disruption_explosion" for e in world.events)
