import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.next_id = 1000
    def _deal_damage(self, *args): pass

class MockBall:
    def __init__(self, id_val=1):
        self.id = id_val
        self.x = 100
        self.y = 100
        self.vx = 0
        self.vy = 0
        self.BALL_TYPE = "sniper"
        self.team = 1
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.base_damage = 10
        self.speed = 50
        self.radius = 15

    def take_damage(self, *args): pass

def test_phantom_artifact_cycle():
    w = MockWorld()
    b = MockBall(1)
    b.has_phantom_artifact = True
    b.phantom_artifact_cooldown = 0.0
    w.balls.append(b)

    a = Action(b, w)

    # Tick 1: Transition to recording
    a.execute("aggressive", 0.1)
    assert b.phantom_artifact_state == "recording"

    # Tick for 5 seconds (50 frames of 0.1 delta)
    for i in range(51):
        b.x = 100 + i
        b.y = 100 + i
        a.execute("aggressive", 0.1)

    # State should be ready after 5 seconds of recording
    assert b.phantom_artifact_state == "ready"
    assert len(b.phantom_artifact_record) == 51
    assert b.phantom_artifact_cooldown == 15.0

    # Now wait for cooldown to expire
    b.phantom_artifact_cooldown = 0.0
    a.execute("aggressive", 0.1)

    # Should spawn a clone and reset state to idle
    assert b.phantom_artifact_state == "idle"
    assert len(w.balls) == 2

    clone = w.balls[1]
    assert clone.is_phantom_artifact_clone
    assert getattr(clone, "has_phantom_artifact", False) == False
    assert clone.damage == 5.0 # 50% damage
    assert clone.hp == 50.0

    # Tick the clone, it should follow the recorded path
    ca = Action(clone, w)
    ca.execute("aggressive", 0.1)

    # Clone should start at the first frame position (x=100, y=100)
    assert clone.x == 100.0
    assert clone.y == 100.0
