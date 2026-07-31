import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 2000.0
        self.hazards = []
        self.platforms = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, y_pos):
        self.id = 1
        self.y = y_pos
        self.hp = 100.0
        self.alive = True
        self.killer = None

def test_vertical_lava_platformer():
    mode = GAME_MODES.get("vertical_lava_platformer")
    assert mode is not None
    assert "lava" in mode.description.lower()
    assert "low_gravity" in mode.mutators

    world = MockWorld()
    balls = [MockBall(1900.0), MockBall(100.0)]

    mode.setup(world, balls)

    # Check bounce pads are generated
    bounce_pads = [h for h in world.arena.hazards if getattr(h, "kind", "") == "bounce_pad"]
    assert len(bounce_pads) == 15

    # Check tick logic
    assert not mode.initialized

    # First tick initializes lava_y to arena height (2000) and then decreases by 15 * delta
    mode.apply_dynamic_traits(world, balls, 1.0) # delta = 1.0

    assert mode.initialized
    assert mode.lava_y == 2000.0 - 15.0 # 1985.0

    # Ball 1 at 1900 is safe
    assert balls[0].hp == 100.0

    # Ball 2 at 100 is safe
    assert balls[1].hp == 100.0

    # Tick again with large delta to raise lava above ball 1
    mode.apply_dynamic_traits(world, balls, 10.0) # lava_y = 1985 - 150 = 1835

    # Ball 1 (1900) should now be in lava (1900 > 1835) and take damage
    assert balls[0].hp == 0.0

    # Tick again to kill ball 1
    mode.apply_dynamic_traits(world, balls, 2.0) # -100 hp
    assert not balls[0].alive
    assert balls[0].killer == "lava"

    # Ball 2 (100) is still safe
    assert balls[1].hp == 100.0
