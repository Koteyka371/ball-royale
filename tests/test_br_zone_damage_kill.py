import sys
sys.path.append('src')
from ai.game_modes import BattleRoyaleMode

class MockWorld:
    def __init__(self):
        self.dead_balls = []

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockBall:
    def __init__(self, id, btype):
        self.id = id
        self.ball_type = btype
        self.alive = True
        self.team = btype
        self.x = 0.0
        self.y = 0.0
        self.hp = 10.0

def test_battle_royale_zone_reverses_time():
    mode = BattleRoyaleMode()
    world = MockWorld()
    world.arena = MockArena()
    balls = [MockBall("b1", "warrior")]


    mode.setup(world, balls)

    # Put ball inside zone to build history
    balls[0].x = 500.0
    balls[0].y = 500.0
    mode.tick(world, balls, delta=1.0) # tick 1

    balls[0].x = 510.0
    mode.tick(world, balls, delta=1.0) # tick 2

    # Put ball outside zone
    balls[0].x = 10000.0
    balls[0].y = 500.0
    mode.tick(world, balls, delta=1.0)

    # Should be reversed to tick 2 position
    assert abs(balls[0].x - 510.0) < 5.0
    assert abs(balls[0].y - 500.0) < 25.0
    assert balls[0].hp == 10.0
    assert balls[0].alive

