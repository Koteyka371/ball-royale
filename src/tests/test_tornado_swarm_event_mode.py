import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

class MockHazard:
    def __init__(self, id, x, y, radius, kind, damage=15.0):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.active = True

def test_tornado_swarm_event_blizzard():
    mode = GAME_MODES["tornado_swarm_event"]
    world = MockWorld()

    # Active event
    mode.active_event = True
    mode.tornado_spawn_timer = 0.0

    # Add ice_patch
    ice = MockHazard(1, 500, 500, 50.0, "ice_patch")
    world.arena.hazards.append(ice)

    # Tick to spawn tornado and trigger combination logic
    mode.tick(world, [], 0.016)

    # Force tornado position to collide with ice_patch
    assert len(world.arena.hazards) > 1
    tornado = world.arena.hazards[1]
    assert tornado.kind in ["mini_tornado", "mini_blizzard"]

    tornado.x = 500.0
    tornado.y = 500.0

    # Tick again for combination
    mode.tick(world, [], 0.016)

    # Check that tornado became mini_blizzard
    assert tornado.kind == "mini_blizzard"
