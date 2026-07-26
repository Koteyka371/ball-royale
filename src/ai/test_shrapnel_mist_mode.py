import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick_timer = 0.0

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100
        self.radius = 20

def test_shrapnel_mist_mode():
    mode = GAME_MODES["shrapnel_mist"]
    world = MockWorld()
    balls = [MockBall(500, 500)]

    # Trigger spawn
    mode.tick(world, balls, 10.0)
    assert len(world.arena.hazards) == 1

    h = world.arena.hazards[0]
    assert h.kind == "shrapnel"
    assert h.split_stage == 0
    assert h.damage == 20.0

    # Tick past split timer, delta must not trigger multiple updates
    mode.tick(world, balls, 3.0)
    assert len(world.arena.hazards) == 3

    for h in world.arena.hazards:
        assert h.kind == "shrapnel"
        assert h.split_stage == 1

    # Tick past next split timer
    mode.tick(world, balls, 2.0)
    assert len(world.arena.hazards) == 9

    for h in world.arena.hazards:
        assert h.kind == "shrapnel"
        assert h.split_stage == 2

    # Tick past final split timer -> turns to mist
    mode.tick(world, balls, 2.0)
    assert len(world.arena.hazards) == 9

    for h in world.arena.hazards:
        assert h.kind == "shrapnel_mist"
        assert hasattr(h, "mist_timer")

    # Remove the 10-second respawn side effect for simpler testing
    mode.spawn_timer = -100.0

    # Tick past mist timer
    mode.tick(world, balls, 5.1)
    assert len(world.arena.hazards) == 0
