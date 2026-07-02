import pytest
from ai.action import Action
from arena.procedural_arena import ProceduralArena, Hazard

class MockBall:
    def __init__(self, x, y):
        self.id = 1
        self.x = x
        self.y = y
        self.radius = 10.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.alive = True

class MockArena(ProceduralArena):
    pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []

def test_vampiric_hazard_drains_max_hp():
    world = MockWorld()
    ball = MockBall(50, 50)
    world.balls.append(ball)

    # Place hazard over the ball
    hazard = Hazard(id=1, x=50, y=50, radius=50, kind="vampiric_puddle", damage=10.0)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)

    # 1 second of draining -> 10 damage to max_hp
    action.execute("idle", 1.0)

    assert ball.max_hp == 90.0
    assert ball.hp == 90.0 # because it gets clamped
    assert getattr(ball, "_vampiric_drained", False)

def test_vampiric_hazard_does_not_drain_out_of_range():
    world = MockWorld()
    ball = MockBall(200, 200) # out of range
    world.balls.append(ball)

    # Place hazard over 50, 50
    hazard = Hazard(id=1, x=50, y=50, radius=50, kind="vampiric_puddle", damage=10.0)
    world.arena.hazards.append(hazard)

    action = Action(ball, world)

    action.execute("idle", 1.0)

    assert ball.max_hp == 100.0
    assert ball.hp == 100.0
    assert not getattr(ball, "_vampiric_drained", False)
