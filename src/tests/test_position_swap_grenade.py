import pytest
from ai.action import Action
from typing import List, Dict, Any

class MockArena:
    def __init__(self):
        self.hazards: List[Any] = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.balls: List[Any] = []
        self.arena = MockArena()
        self.events: List[Dict[str, Any]] = []

class MockBall:
    def __init__(self, id, x, y, team, hp=100.0):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = hp
        self.alive = True
        self.radius = 10.0
        self.skill_cooldown = 5.0
        self.skill_timer = 0.0

class MockHazard:
    def __init__(self, kind, x, y, owner_id=None, team=None):
        self.kind = kind
        self.x = x
        self.y = y
        self.owner_id = owner_id
        self.team = team
        self.duration = 2.0
        self.vx = 0.0
        self.vy = 0.0
        self.active = True

def test_throw_position_swap_grenade_deployment():
    world = MockWorld()
    ball = MockBall(id="b1", x=100.0, y=100.0, team="team_A")
    enemy = MockBall(id="b2", x=200.0, y=100.0, team="team_B")
    world.balls = [ball, enemy]

    action = Action(ball, world)
    action.ball.active_skill = "throw_position_swap_grenade"
    action._use_skill()

    # Assert hazard is spawned
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "thrown_position_swap_grenade"
    assert getattr(hazard, "owner_id", None) == ball.id
    assert getattr(hazard, "duration", 0.0) == 2.0
    assert getattr(hazard, "vx", 0.0) > 0  # Should be thrown towards enemy at (200, 100)

def test_throw_position_swap_grenade_explosion_with_enemy():
    world = MockWorld()
    ball = MockBall(id="b1", x=10.0, y=10.0, team="team_A")
    enemy = MockBall(id="b2", x=100.0, y=100.0, team="team_B")
    world.balls = [ball, enemy]

    hazard = MockHazard("thrown_position_swap_grenade", x=100.0, y=110.0, owner_id=ball.id, team=ball.team)
    hazard.duration = 0.01
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    # This should tick the hazard down to <= 0 and explode
    action.ball.active_skill = "idle"
    action.execute("attack", 0.1)

    # Hazard should be removed
    assert len(world.arena.hazards) == 0

    # Positions should be swapped
    assert abs(ball.x - 100.0) < 1.0
    assert abs(ball.y - 100.0) < 1.0
    assert abs(enemy.x - 10.0) < 1.0
    assert abs(enemy.y - 10.0) < 1.0

    # Event should be recorded
    swap_events = [e for e in world.events if e["type"] == "position_swapped"]
    assert len(swap_events) == 1
    assert swap_events[0]["data"]["ball_a"] == ball.id
    assert swap_events[0]["data"]["ball_b"] == enemy.id

def test_throw_position_swap_grenade_explosion_no_enemy():
    world = MockWorld()
    ball = MockBall(id="b1", x=10.0, y=10.0, team="team_A")
    # Enemy is too far away
    enemy = MockBall(id="b2", x=500.0, y=500.0, team="team_B")
    world.balls = [ball, enemy]

    hazard = MockHazard("thrown_position_swap_grenade", x=100.0, y=100.0, owner_id=ball.id, team=ball.team)
    hazard.duration = 0.01
    world.arena.hazards.append(hazard)

    action = Action(ball, world)
    action.ball.active_skill = "idle"
    action.execute("attack", 0.1)

    # Positions should NOT be swapped
    assert abs(ball.x - 10.0) < 1.0
    assert abs(enemy.x - 500.0) < 1.0

    # No swap event
    swap_events = [e for e in world.events if e["type"] == "position_swapped"]
    assert len(swap_events) == 0
