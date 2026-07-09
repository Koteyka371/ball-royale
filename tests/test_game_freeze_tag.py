import sys
import os
sys.path.insert(0, os.path.abspath('src'))

from ai.game_modes import FreezeTagMode

class MockBall:
    def __init__(self, x=0, y=0, radius=10, vx=0, vy=0, alive=True, ball_type="player"):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = vx
        self.vy = vy
        self.alive = alive
        self.ball_type = ball_type
        self.is_frozen = False
        self.stun_timer = 0.0
        self.frozen_timer = 0.0
        self.team = None

class MockWorld:
    def __init__(self):
        self.dead_balls = []

def test_freeze_tag_setup():
    mode = FreezeTagMode()
    world = MockWorld()
    balls = [MockBall() for _ in range(4)]
    mode.setup(world, balls)

    # First half Red, second half Blue
    assert balls[0].team == "Red"
    assert balls[1].team == "Red"
    assert balls[2].team == "Blue"
    assert balls[3].team == "Blue"

    for b in balls:
        assert b.is_frozen == False

def test_collision_freezes_enemy():
    mode = FreezeTagMode()
    world = MockWorld()

    # Two enemies colliding
    b1 = MockBall(x=10, y=10, vx=50, vy=0)
    b1.team = "Red"

    b2 = MockBall(x=15, y=10, vx=10, vy=0)
    b2.team = "Blue"

    balls = [b1, b2]
    mode.tick(world, balls, delta=0.016)

    # b1 is faster (v=50 vs v=10), so b2 gets frozen
    assert b1.is_frozen == False
    assert b2.is_frozen == True
    assert b2.stun_timer == 9999.0
    assert b2.frozen_timer == 9999.0
    assert b2.vx == 0.0
    assert b2.vy == 0.0

def test_collision_unfreezes_ally():
    mode = FreezeTagMode()
    world = MockWorld()

    # Two allies colliding
    b1 = MockBall(x=10, y=10)
    b1.team = "Red"
    b1.is_frozen = True
    b1.stun_timer = 9999.0
    b1.frozen_timer = 9999.0

    b2 = MockBall(x=15, y=10)
    b2.team = "Red"
    b2.is_frozen = False

    balls = [b1, b2]
    mode.tick(world, balls, delta=0.016)

    # b2 should unfreeze b1
    assert b1.is_frozen == False
    assert b1.stun_timer == 0.0
    assert b1.frozen_timer == 0.0
    assert b2.is_frozen == False

def test_check_winner_logic():
    mode = FreezeTagMode()
    world = MockWorld()

    b1 = MockBall()
    b1.team = "Red"
    b1.is_frozen = True

    b2 = MockBall()
    b2.team = "Red"
    b2.is_frozen = True

    b3 = MockBall()
    b3.team = "Blue"
    b3.is_frozen = False

    balls = [b1, b2, b3]

    # Red is all frozen, Blue is active
    winner = mode.check_winner(world, balls)
    assert winner == "Blue"

    # If Blue is also frozen
    b3.is_frozen = True
    winner = mode.check_winner(world, balls)
    assert winner == "Draw"

if __name__ == "__main__":
    test_freeze_tag_setup()
    test_collision_freezes_enemy()
    test_collision_unfreezes_ally()
    test_check_winner_logic()
    print("All tests passed!")
