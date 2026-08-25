import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.events = []

class MockArena:
    def __init__(self):
        self.hazards = []

class MockEntity:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True
        self.radius = 15.0

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.speed = 2.0
        self.damage = 10.0
        self.hp = 100.0

def test_blood_pact_artifact():
    world = MockWorld()
    artifact = MockEntity(0, 0, "blood_pact_artifact_item")
    world.boosters.append(artifact)
    ball = MockBall()
    action = Action(ball, world)

    # Pre-artifact stats
    assert ball.speed == 2.0
    assert ball.damage == 10.0
    assert ball.hp == 100.0

    # Collect artifact
    action._collect_booster(1.0)

    # Assert collected
    assert not artifact.active
    assert getattr(ball, "has_blood_pact_artifact", False) == True

    # Tick
    action.execute("idle", 1.0)

    # Assert stats doubled and applied
    assert ball.blood_pact_artifact_applied == True
    assert ball.speed == 4.0
    assert ball.damage == 20.0
    # Health drained by 3.0 * delta
    assert ball.hp == 97.0

    # Tick again
    action.execute("idle", 1.0)
    # Stats shouldn't double again
    assert ball.speed == 4.0
    assert ball.damage == 20.0
    # Health drains again
    assert ball.hp == 94.0
