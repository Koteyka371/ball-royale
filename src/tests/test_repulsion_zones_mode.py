import pytest
from ai.game_modes import GameMode, RepulsionZonesMode

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.ball_type = "player"

class MockArena:
    def __init__(self):
        self.width = 800
        self.height = 800
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockHazard:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 100.0
        self.kind = "repulsion_zone"
        self.duration = 10.0

def test_repulsion_zones_mode_setup():
    mode = RepulsionZonesMode()
    world = MockWorld()
    mode.setup(world, [])
    assert world.arena.hazards == []

def test_repulsion_zones_mode_tick_spawns_hazards():
    mode = RepulsionZonesMode()
    world = MockWorld()
    mode.setup(world, [])

    # Tick past 5 seconds
    for _ in range(500):
        mode.tick(world, [], 0.016)

    assert len(world.arena.hazards) > 0
    assert getattr(world.arena.hazards[0], "kind", "") == "repulsion_zone"

def test_repulsion_zones_mode_pushes_players_away():
    mode = RepulsionZonesMode()
    world = MockWorld()
    b = MockBall(400, 400)
    mode.setup(world, [b])

    h = MockHazard(400, 400)
    world.arena.hazards.append(h)

    # Place ball slightly to the right of center
    b.x = 450
    b.y = 400

    # Tick once
    mode.tick(world, [b], 0.016)

    # Check if pushed to the right
    assert b.vx > 0
    assert b.vy == 0
