import pytest
from ai.game_modes import OutsideInFallingTilesMode

class MockArena:
    def __init__(self, width=1000.0, height=1000.0):
        self.width = width
        self.height = height

class MockWorld:
    def __init__(self, arena_w=1000.0, arena_h=1000.0):
        self.arena = MockArena(arena_w, arena_h)
        self.events = []

    def add_event(self, event_type, payload):
        self.events.append((event_type, payload))

class MockBall:
    def __init__(self, x=500.0, y=500.0):
        self.id = 1
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "player"
        self.hp = 100.0

def test_outside_in_falling_tiles_setup():
    mode = OutsideInFallingTilesMode()
    world = MockWorld(1000.0, 1000.0)
    mode.setup(world, [])

    assert mode.phase == "wait"
    assert mode.timer == 5.0
    assert mode.current_ring == 0
    assert mode.cols == 20 # 1000 / 50
    assert mode.rows == 20 # 1000 / 50

    # Check that all tiles are normal
    for c in range(20):
        for r in range(20):
            assert mode.tiles[(c, r)]["state"] == "normal"

def test_outside_in_falling_tiles_phases():
    mode = OutsideInFallingTilesMode()
    world = MockWorld(200.0, 200.0) # 4x4 grid (0,1,2,3)
    mode.setup(world, [])

    assert mode.cols == 4
    assert mode.rows == 4

    # Tick 5 seconds to transition to warning phase
    mode.tick(world, [], 5.0)

    assert mode.phase == "warning"
    assert mode.timer == 2.0

    # The first ring should be the outer edges (c=0,3 and r=0,3)
    # Total tiles = 16. Outer ring = 12 tiles
    assert len(mode.falling_tiles) == 12

    # Check if outer tiles are in warning state
    assert mode.tiles[(0, 0)]["state"] == "warning"
    assert mode.tiles[(3, 3)]["state"] == "warning"

    # Tick 2 seconds to transition to falling phase
    mode.tick(world, [], 2.0)

    assert mode.phase == "falling"
    assert mode.timer == 3.0
    assert mode.tiles[(0, 0)]["state"] == "falling"

    # Tick 3 seconds to transition to wait phase and turn to pit
    mode.tick(world, [], 3.0)

    assert mode.phase == "wait"
    assert mode.timer == 5.0
    assert mode.tiles[(0, 0)]["state"] == "pit"
    assert mode.current_ring == 1

def test_outside_in_falling_tiles_damage():
    mode = OutsideInFallingTilesMode()
    world = MockWorld(200.0, 200.0)
    b = MockBall(25.0, 25.0) # Will be in tile (0, 0)
    mode.setup(world, [b])

    # Set tile (0, 0) directly to pit to test damage
    mode.tiles[(0, 0)]["state"] = "pit"

    mode.tick(world, [b], 0.1)

    assert b.alive == False
    assert b.hp == 0.0

if __name__ == '__main__':
    pytest.main(['-s', __file__])
