import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.time = 0.0

class MockBall:
    def __init__(self):
        self.id = 1
        self.team = "Red"
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.speed = 2.0
        self.emotion = "neutral"
        self.slime_trail_timer = 0.0

def test_slime_trail_creation():
    world = MockWorld()
    ball = MockBall()
    ball.slime_trail_timer = 0.0
    action = Action(ball, world)

    # Run _flee
    action._get_enemies = lambda: [type("E", (), {"x": 10.0, "y": 10.0})()]
    action._get_allies = lambda: []

    action._flee(0.1)

    slimes = [h for h in world.arena.hazards if h.kind == "slime"]
    assert len(slimes) == 1
    assert slimes[0].owner_id == ball.id

    # Another frame shouldn't spawn slime since timer is 0.5
    action._flee(0.1)
    slimes = [h for h in world.arena.hazards if h.kind == "slime"]
    assert len(slimes) == 1

    # Fast forward
    action.ball.slime_trail_timer = 0.0
    action._flee(0.1)
    slimes = [h for h in world.arena.hazards if h.kind == "slime"]
    assert len(slimes) == 2

def test_slime_hazard_slows_enemy():
    world = MockWorld()
    ball = MockBall()
    ball.id = 2
    ball.team = "Blue"
    action = Action(ball, world)

    class Slime:
        kind = "slime"
        x = 0.0
        y = 0.0
        radius = 12.0
        owner_id = 1
        team = "Red"

    world.arena.hazards.append(Slime())

    action.execute("idle", 0.1)

    assert getattr(ball, "speed_debuff_timer", 0.0) > 0.0
    assert getattr(ball, "speed_debuff_multiplier", 1.0) == 0.5

    # Should not slow down ally
    ball.team = "Red"
    ball.speed_debuff_timer = 0.0
    ball.speed_debuff_multiplier = 1.0

    action.execute("idle", 0.1)

    assert getattr(ball, "speed_debuff_timer", 0.0) == 0.0
    assert getattr(ball, "speed_debuff_multiplier", 1.0) == 1.0
