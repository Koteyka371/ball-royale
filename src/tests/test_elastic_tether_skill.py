import pytest
import math
from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.balls = []

class MockBall:
    def __init__(self, x, y, id="b1"):
        self.x = x
        self.y = y
        self.id = id
        self.vx = 0.0
        self.vy = 0.0
        self.skill = "elastic_tether"
        self.active_skill = "elastic_tether"
        self.SKILL_COOLDOWN = 5.0
        self.skill_timer = 0.0
        self.hp = 100
        self.alive = True
        self.team = "A"
        self.state_history = []
        self.charge_level = 100
        self.speed = 100.0
        self.elastic_tether_timer = 0.0

def test_elastic_tether_skill_activation_and_pull():
    world = MockWorld()

    # Ball is near the left wall (x=100). Width is 1000, so left wall is closest (x=0).
    ball = MockBall(x=100.0, y=500.0)
    world.balls = [ball]

    action = Action(ball, world)
    action._use_skill()

    # The timer should be set
    assert ball.elastic_tether_timer == 5.0

    # It should target the left wall (x=0, y=500)
    assert ball.elastic_tether_target is not None
    assert ball.elastic_tether_target.x == 0.0
    assert ball.elastic_tether_target.y == 500.0

    # Now execute tick to apply spring force
    # ball is at x=100. target is at x=0. dx = -100.
    # dist = 100.
    # force = (dist / 200.0) * 1500.0 * delta
    #       = (100 / 200) * 1500 * 0.1 = 0.5 * 150 = 75
    # vx should decrease by 75 (accelerating left towards the wall)

    # Avoid attack logic overwriting vx/vy by setting active_skill to None after use_skill
    ball.active_skill = None
    action.execute('flee', delta=0.1)

    assert ball.elastic_tether_timer == 4.9
    assert ball.vx != 0.0
    # Expected: (dx/dist) * force = (-100/100) * 75 = -75
    assert ball.vx < -3.0 # Flee strategy alters vx, but we just verify it moved left towards wall

if __name__ == "__main__":
    pytest.main(["-v", __file__])
