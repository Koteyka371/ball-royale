from ai.action import Action
import pytest

class MockBall:
    def __init__(self, x=0, y=0, team="red", speed=2.0):
        self.x = x
        self.y = y
        self.team = team
        self.speed = speed
        self.base_speed = speed
        self.skill = "mirror_stance"
        self.skill_timer = 0
        self.active_skill = "mirror_stance"
        self.id = 1
        self.alive = True

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = None
        self.time = 0.0

    def _deal_damage(self, attacker, target):
        pass

def test_mirror_stance_skill():
    ball = MockBall()
    world = MockWorld()
    world.balls.append(ball)
    action = Action(ball, world)

    # ensure default states
    assert getattr(ball, "reflect_shield_active", False) == False
    assert getattr(ball, "mirror_stance_timer", 0.0) == 0.0

    # execute skill
    action.execute("use_skill", 0.1)

    # check if activated correctly
    assert getattr(ball, "reflect_shield_active", False) == True
    assert getattr(ball, "reflect_shield_timer", 0.0) > 0.0
    assert getattr(ball, "mirror_stance_timer", 0.0) > 0.0

    # simulate tick to check speed
    action.execute("idle", 0.1)

    assert ball.speed == ball.base_speed * 0.5

    # simulate expiration
    ball.mirror_stance_timer = 0.1
    action.execute("idle", 0.2)

    assert getattr(ball, "mirror_stance_active", False) == False
    assert ball.speed == ball.base_speed
