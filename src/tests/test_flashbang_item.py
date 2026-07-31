from ai.action import Action
import math

class MockBall:
    def __init__(self, id, team, x, y, ball_type="basic"):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = ball_type
        self.perception_radius = 500.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = type('obj', (object,), {'hazards': []})

def test_flashbang_item_use():
    ball = MockBall(1, "teamA", 0, 0)
    enemy = MockBall(2, "teamB", 100, 0)
    far_enemy = MockBall(3, "teamB", 300, 0)
    world = MockWorld()
    world.balls = [ball, enemy, far_enemy]

    ball.inventory = ["flashbang_item"]
    ball.use_item = True

    action = Action(ball, world)
    action.execute("attack", 0.016)

    # Enemy in radius should be blinded, stunned, and 0 perception radius
    assert getattr(enemy, "is_blinded", False)
    assert getattr(enemy, "blindness_timer", 0.0) >= 3.0
    assert getattr(enemy, "is_stunned", False)
    assert getattr(enemy, "stun_timer", 0.0) >= 1.0
    assert enemy.perception_radius == 0.0

    # Far enemy should be unaffected
    assert not getattr(far_enemy, "is_blinded", False)
    assert getattr(far_enemy, "blindness_timer", 0.0) == 0.0
    assert not getattr(far_enemy, "is_stunned", False)
    assert getattr(far_enemy, "stun_timer", 0.0) == 0.0
    assert far_enemy.perception_radius == 500.0

    assert "flashbang_item" not in ball.inventory
    assert not ball.use_item
