from ai.spiderman import SpidermanMode

class MockArena:
    def __init__(self):
        self.base_friction = 1.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

class MockBall:
    def __init__(self):
        self.inventory = []
        self.is_frictionless = False
        self.friction_multiplier = 1.0
        self.alive = True

def test_spiderman_mode_setup():
    mode = SpidermanMode()
    world = MockWorld()
    ball = MockBall()
    mode.setup(world, [ball])

    assert world.arena.base_friction == 0.0
    assert "grapple_hook" in ball.inventory
    assert ball.is_frictionless == True
    assert ball.friction_multiplier == 0.0

def test_spiderman_mode_tick():
    mode = SpidermanMode()
    world = MockWorld()
    ball = MockBall()
    mode.setup(world, [ball])

    ball.inventory.remove("grapple_hook")
    ball.is_frictionless = False

    mode.tick(world, [ball], 0.1)

    assert "grapple_hook" in ball.inventory
    assert ball.is_frictionless == True

print("Test script ready")
