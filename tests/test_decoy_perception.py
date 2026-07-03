from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = None
        self.balls = []

class MockBall:
    def __init__(self, bid, x=0, y=0, ball_type="default"):
        self.x = x
        self.y = y
        self.id = bid
        self.ball_type = ball_type
        self.alive = True
        self.is_decoy = False

def test_decoy_perception_check():
    world = MockWorld()

    # enemy_id = 1, decoy_id = 1 => 32 % 100 = 32. 32 > 50 is False => passes check => ignores decoy.
    ball1 = MockBall(1, x=0, y=0, ball_type="typeA")
    decoy1 = MockBall(1, x=10, y=10, ball_type="typeB")
    decoy1.is_decoy = True

    # enemy_id = 2, decoy_id = 1 => 63 % 100 = 63. 63 > 50 is True => fails check => targets decoy.
    ball2 = MockBall(2, x=0, y=0, ball_type="typeA")

    world.balls = [ball1, ball2, decoy1]

    action1 = Action(ball1, world)
    enemies1 = action1._get_enemies()
    assert len(enemies1) == 0, f"Ball 1 should ignore decoy 1, got {len(enemies1)} enemies"

    action2 = Action(ball2, world)
    enemies2 = action2._get_enemies()
    assert len(enemies2) == 1, f"Ball 2 should target decoy 1, got {len(enemies2)} enemies"
    assert enemies2[0] == decoy1
