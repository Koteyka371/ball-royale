import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.team = "team"
        self.ball_type = "mock"
        self.is_decoy = False
        self.skill_timer = 0.0
        self.base_speed = 0.0
        self.speed = 0.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.next_id = 9000

def test_decoy_swap_survival():
    world = MockWorld()

    ball = MockBall(1, 100, 100)
    ball.skill = "decoy_swap_survival"
    ball.SKILL = "decoy_swap_survival"
    ball.SKILL_COOLDOWN = 8.0

    world.balls = [ball]

    action = Action(ball, world)

    # Let action use skill
    action._use_skill()
    action.execute("idle", 0.1)

    # Should have spawned a decoy at the same position
    assert len(world.balls) == 2
    decoy = world.balls[1]
    assert decoy.is_decoy is True
    assert decoy.x == 100
    assert decoy.y == 100
    assert decoy.decoy_timer == 3.5
    assert getattr(ball, "survival_swap_target_id", None) == decoy.id
    # Since timer was initialized to 3.0 and then execute ran which decremented it by 0.1:
    assert getattr(ball, "survival_swap_timer", 0.0) == 2.9

    # Now move the ball
    ball.x = 200
    ball.y = 200

    # Wait out the rest of the timer
    action.execute("idle", 2.9)

    # After timer reaches <= 0, they should swap
    assert getattr(ball, "survival_swap_timer", 0.0) == 0.0

    # Decoy should now be at ball's old position (200, 200) and dead
    assert decoy.x == 200
    assert decoy.y == 200
    assert decoy.hp == 0
    assert decoy.alive is False

    # Ball should now be at decoy's old position (100, 100)
    assert ball.x == 100
    assert ball.y == 100
