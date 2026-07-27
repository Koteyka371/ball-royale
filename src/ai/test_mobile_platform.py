import pytest
from ai.game_modes import GAME_MODES, GameMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.balls = []

class MockBall:
    def __init__(self, id_val, x, y, is_turret=False):
        self.id = id_val
        self.x = x
        self.y = y
        self.is_turret = is_turret
        self.alive = True

def test_mobile_platform_mode():
    mode = GAME_MODES.get("mobile_platform")
    if not mode:
        pytest.skip("Mode not implemented yet")

    world = MockWorld()

    mode.setup(world, [])

    assert len(world.arena.hazards) == 1
    platform = world.arena.hazards[0]
    assert platform.kind == "mobile_platform"

    old_x, old_y = platform.x, platform.y

    turret1 = MockBall(1, old_x, old_y, is_turret=True)
    turret2 = MockBall(2, 900, 900, is_turret=True) # Outside
    player = MockBall(3, old_x, old_y, is_turret=False) # Inside, but not a turret

    world.balls = [turret1, turret2, player]

    mode.tick(world, world.balls, 0.1)

    assert platform.x != old_x or platform.y != old_y
    dx = platform.x - old_x
    dy = platform.y - old_y

    # turret1 should move with the platform
    assert turret1.x == pytest.approx(old_x + dx)
    assert turret1.y == pytest.approx(old_y + dy)

    # turret2 should not move
    assert turret2.x == 900
    assert turret2.y == 900

    # player should not move
    assert player.x == old_x
    assert player.y == old_y
