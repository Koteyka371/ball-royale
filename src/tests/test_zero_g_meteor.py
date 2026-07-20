import sys

import math
sys.path.append('src')

from ai.game_modes import ZeroGravityMeteorShowerMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x=500.0, y=500.0):
        self.x = x
        self.y = y
        self.radius = 20.0
        self.hp = 100.0
        self.alive = True

def test_zero_g_meteor_bouncing():
    mode = ZeroGravityMeteorShowerMode()
    world = MockWorld()
    ball = MockBall()

    mode.setup(world, [ball])

    # Fast forward time to spawn meteors and trigger zero gravity
    for _ in range(600):
        mode.apply_dynamic_traits(world, [ball], 0.01)

    assert mode.is_zero_g == True
    assert "zero_gravity" in mode.mutators

    meteors = [h for h in world.arena.hazards if getattr(h, "kind", "") == "meteor"]
    assert len(meteors) > 0

    # Setup a specific meteor for bounce testing
    m = meteors[0]
    m.x = 10.0
    m.y = 500.0
    m.vx = -100.0
    m.vy = 0.0
    m.radius = 30.0

    # Tick to cause boundary collision on left wall
    mode.apply_dynamic_traits(world, [ball], 0.1)

    assert m.x >= m.radius
    assert m.vx > 0  # Bounced off the wall, velocity reversed

if __name__ == '__main__':
    test_zero_g_meteor_bouncing()
