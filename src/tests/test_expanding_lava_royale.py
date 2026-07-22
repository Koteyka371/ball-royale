import math
from ai.game_modes import ExpandingLavaRoyaleMode

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
    def __init__(self, t):
        self.ball_type = t
        self.alive = True
        self.hp = 100.0
        self.x = 500.0
        self.y = 500.0
        self.vx = 0.0
        self.vy = 0.0
        self.team = t
        self.burn_timer = 0.0
        self.weather_immunity_timer = 0.0

def test_expanding_lava_royale_mode():
    mode = ExpandingLavaRoyaleMode()
    world = MockWorld()

    b1 = MockBall("warrior")
    b1.x = 500.0
    b1.y = 500.0

    b2 = MockBall("scout")
    b2.x = 100.0
    b2.y = 100.0

    mode.setup(world, [b1, b2])

    assert mode.danger_radius == 50.0
    assert len(world.arena.hazards) == 0

    # Tick 1 - b1 should take damage because it is exactly at 500,500
    # b2 should not take damage
    mode.tick(world, [b1, b2], 1.0)

    assert mode.danger_radius == 65.0
    assert b1.hp == 75.0 # 100 - 25*1
    assert b1.burn_timer == 1.0
    assert b2.hp == 100.0

    # Fast forward, tick enough for hazard spawn (timer = 3.0 at setup)
    mode.tick(world, [b1, b2], 2.1)

    # Should spawn hazard
    assert len(world.arena.hazards) >= 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "fire_zone"
