import math
from ai.game_modes import MobilePlatformMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y, is_turret):
        self.id = id
        self.x = x
        self.y = y
        self.is_turret = is_turret
        self.alive = True
        self.owner_id = None

def test_mobile_platform():
    world = MockWorld()
    balls = []

    mode = MobilePlatformMode()
    mode.setup(world, balls)

    platform = mode.platform
    assert platform is not None
    assert len(world.arena.hazards) == 1

    platform.x = 500
    platform.y = 500
    platform.vx = 100
    platform.vy = 0

    turret1 = MockBall(1, 500, 500, True) # On platform
    turret2 = MockBall(2, 500, 700, True) # Off platform
    non_turret = MockBall(3, 500, 500, False) # On platform but not turret

    balls.extend([turret1, turret2, non_turret])

    mode.tick(world, balls, 1.0) # Move 100 units right

    assert platform.x == 600
    assert turret1.x == 600
    assert turret1.y == 500
    assert turret2.x == 500
    assert non_turret.x == 500

    print("Python Mobile Platform test passed")

if __name__ == '__main__':
    test_mobile_platform()
