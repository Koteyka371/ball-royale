import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ai.game_modes import GAME_MODES, StickyArenaMode

class MockArena:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y):
        self.alive = True
        self.x = x
        self.y = y
        self.radius = 10.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.vx = 100.0
        self.vy = 100.0

def test_sticky_arena_mode_setup():
    mode = StickyArenaMode()
    world = MockWorld()
    balls = [MockBall(400, 300)]
    mode.setup(world, balls)

    # Check glue patches spawned
    glue_patches = [h for h in world.arena.hazards if getattr(h, "kind", "") == "glue_patch"]
    assert len(glue_patches) >= 5, "Should spawn at least 5 glue patches"

def test_sticky_arena_mode_tick_glue():
    mode = StickyArenaMode()
    world = MockWorld()
    b = MockBall(400, 300)
    balls = [b]

    class MockHazard:
        def __init__(self, x, y, r, kind):
            self.x = x
            self.y = y
            self.radius = r
            self.kind = kind

    world.arena.hazards.append(MockHazard(400, 300, 50.0, "glue_patch"))

    # Verify inside glue dampens velocity and speed
    mode.tick(world, balls, 0.016)

    assert b.speed == 50.0, "Speed should be 50% of base speed"
    assert b.vx == 95.0, "vx should be dampened by 0.95"
    assert b.vy == 95.0, "vy should be dampened by 0.95"

def test_sticky_arena_mode_tick_wall():
    mode = StickyArenaMode()
    world = MockWorld()
    # Ball is very close to wall
    b = MockBall(5, 300)
    b.vx = 100.0
    b.vy = 100.0
    balls = [b]

    mode.tick(world, balls, 0.016)

    assert b.vx == 80.0, "vx should be dampened by 0.8 at wall"
    assert b.vy == 80.0, "vy should be dampened by 0.8 at wall"
