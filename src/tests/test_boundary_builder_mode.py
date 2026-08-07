import pytest
from ai.game_modes import BoundaryBuilderMode

class MockArena:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.hazards = []

class MockWorld:
    def __init__(self, w, h):
        self.arena = MockArena(w, h)
        self.events = []

    def add_event(self, event_name, event_data=None):
        self.events.append((event_name, event_data))

class MockBall:
    def __init__(self, id, team, ball_type="player"):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.x = 0
        self.y = 0
        self.radius = 15.0
        self.alive = True
        self.blocks_collected = 0

def test_boundary_builder_mode_resource_spawning():
    mode = BoundaryBuilderMode()
    world = MockWorld(1000, 1000)
    balls = []

    mode.tick(world, balls, delta=5.0)

    # Should have spawned 1 resource block
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "resource_block"

def test_boundary_builder_mode_collection():
    mode = BoundaryBuilderMode()
    world = MockWorld(1000, 1000)
    b1 = MockBall(1, "red")
    b1.x = 500
    b1.y = 500
    balls = [b1]

    # manually add 1 block at same pos
    world.arena.hazards.append(mode.ResourceBlock(1000, 500, 500))

    mode.tick(world, balls, delta=0.1)

    # block should be collected and removed
    assert len(world.arena.hazards) == 0
    assert b1.blocks_collected == 1

def test_boundary_builder_mode_rebuild_bunker():
    mode = BoundaryBuilderMode()
    world = MockWorld(1000, 1000)
    b1 = MockBall(1, "red")
    b1.x = 500
    b1.y = 500
    b1.blocks_collected = 2
    balls = [b1]

    world.arena.hazards.append(mode.ResourceBlock(1000, 500, 500))

    mode.tick(world, balls, delta=0.1)

    assert b1.blocks_collected == 0
    # arena should expand
    assert world.arena.width == 1050.0
    assert world.arena.height == 1050.0

    # bunker should be built
    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "bunker"
    assert world.arena.hazards[0].team == "red"

def test_boundary_builder_mode_bunker_collision():
    mode = BoundaryBuilderMode()
    world = MockWorld(1000, 1000)

    b1 = MockBall(1, "blue")
    b1.x = 520
    b1.y = 500
    balls = [b1]

    bunker = mode.Bunker(2000, "red", 500, 500)
    world.arena.hazards.append(bunker)

    mode.tick(world, balls, delta=1.0)

    # b1 should be pushed away
    import math
    dist = math.hypot(b1.x - 500, b1.y - 500)
    assert dist >= 55.0  # bunker radius (40) + ball radius (15)

    # bunker hp decreases
    assert bunker.hp < 500.0
