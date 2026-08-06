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
        self.team = "teamA"
        self.ball_type = "mock"
        self.is_decoy = False
        self.skill_timer = 0.0
        self.base_speed = 0.0
        self.speed = 0.0
        self.is_confused = False
        self.confusion_timer = 0.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.next_id = 9000

def test_decoy_chain_surge():
    world = MockWorld()

    ball = MockBall(1, 100, 100)

    decoy1 = MockBall(2, 200, 200)
    decoy1.is_decoy = True
    decoy1.owner_id = 1

    decoy2 = MockBall(3, 300, 300)
    decoy2.is_decoy = True
    decoy2.owner_id = 1

    enemy = MockBall(4, 210, 210)
    enemy.team = "teamB"
    enemy.is_confused = False
    enemy.confusion_timer = 0.0

    ball.survival_swap_target_id = decoy1.id
    ball.survival_swap_timer = 0.1

    world.balls = [ball, decoy1, decoy2, enemy]

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert ball.survival_swap_timer == 0.0

    # Decoys should be dead
    assert decoy1.alive is False
    assert decoy1.hp == 0
    assert decoy2.alive is False
    assert decoy2.hp == 0

    # Ball should not have swapped because surge happened
    assert ball.x == 100
    assert ball.y == 100

    # Enemy takes damage from multiple decoys since both trigger a search
    # enemy is close enough to both decoy 1 (10 units) and decoy 2 (127 units), so it takes 60 damage
    assert enemy.hp < 100
    assert enemy.is_confused is True
    assert enemy.confusion_timer in [3.0, 4.0]
