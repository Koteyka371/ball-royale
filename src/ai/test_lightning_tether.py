import pytest
from ai.action import Action
from ai.ball_types_lightning_tether import LightningTetherBall

class MockWorld:
    def __init__(self):
        self.balls = []

    def get_nearby_entities(self, b, r):
        return {"enemies": [e for e in self.balls if getattr(e, "team", "") != getattr(b, "team", "")], "allies": []}

def test_lightning_tether():
    world = MockWorld()
    tether = LightningTetherBall(1, 0, 0)
    tether.team = "A"
    tether.hp = 100.0

    class MockEnemy:
        def __init__(self, id, x, y):
            self.id = id
            self.x = x
            self.y = y
            self.hp = 100.0
            self.team = "B"
            self.alive = True

    e1 = MockEnemy(2, 50, 0)
    e2 = MockEnemy(3, 100, 0)
    e3 = MockEnemy(4, 250, 0) # out of chain range from e1

    world.balls = [tether, e1, e2, e3]

    action = Action(tether, world)

    # Use skill
    action._use_skill()
    action._update_skill_timer(0.0)

    assert tether.lightning_tether_timer > 0.0
    assert tether.lightning_tether_target == e1

    # Simulate tick
    action.execute("idle", 0.1)

    # Damage should be dealt to e1 and chained to e2
    assert e1.hp < 100.0
    assert e1.hp == 100.0 - 15.0 * 0.1
    assert e2.hp == 100.0 - 7.5 * 0.1
    assert e3.hp == 100.0
