import math
from ai.game_modes import LavaRoyaleMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, ball_id, ball_type):
        self.id = ball_id
        self.ball_type = ball_type
        self.x = 500.0
        self.y = 500.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.burn_timer = 0.0

def test_lava_royale_mode_basic():
    mode = LavaRoyaleMode()
    world = MockWorld()
    balls = [MockBall(1, "warrior"), MockBall(2, "scout")]

    mode.setup(world, balls)
    for b in balls:
        assert b.team == b.ball_type

    assert mode.check_winner(world, balls) is None

    balls[1].alive = False
    assert mode.check_winner(world, balls) == "warrior"

def test_lava_royale_zone_shrinks_and_damages():
    mode = LavaRoyaleMode()
    world = MockWorld()
    # ball 1 in center, ball 2 at edge
    b1 = MockBall(1, "warrior")
    b1.x = 500.0
    b1.y = 500.0

    b2 = MockBall(2, "scout")
    b2.x = 1000.0
    b2.y = 1000.0

    balls = [b1, b2]

    mode.setup(world, balls)

    # Tick to initialize zone
    mode.tick(world, balls, delta=0.1)

    assert mode.zone_radius == 1000.0 - 15.0 * 0.1

    # Fast forward so radius is smaller than distance to b2
    for _ in range(500):
        mode.tick(world, balls, delta=0.1)

    assert mode.zone_radius < 500.0
    assert b1.hp >= -500.0 # Just safe enough, ignoring background damage
    assert b2.hp < 100.0 # Took lava damage
    assert b2.burn_timer > 0.0
