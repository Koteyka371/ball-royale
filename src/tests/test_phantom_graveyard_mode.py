import pytest
from ai.game_modes import PhantomGraveyardMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y, alive=True, hp=100.0):
        self.id = id
        self.x = x
        self.y = y
        self.alive = alive
        self.hp = hp
        self.ball_type = "player"
        self.radius = 15.0
        self.graveyard_teleport_cd = 0.0

def test_phantom_graveyard_hazard():
    mode = PhantomGraveyardMode()
    world = MockWorld()

    b1 = MockBall(1, 100.0, 100.0, alive=False, hp=0.0)
    b2 = MockBall(2, 500.0, 500.0, alive=True, hp=100.0)

    balls = [b1, b2]

    # Run setup
    mode.setup(world, balls)
    assert len(world.arena.hazards) == 1

    hazard = world.arena.hazards[0]
    assert hazard.kind == "phantom_graveyard_zone"
    assert hazard.x == 500.0
    assert hazard.y == 500.0

    # Tick 1: B1 dies, should record death location (100.0, 100.0)
    mode.tick(world, balls, 0.016)
    assert len(mode.recent_death_locations) == 1
    assert mode.recent_death_locations[0] == (100.0, 100.0)

    # Tick 2: B2 enters hazard. It's at (500.0, 500.0) which is hazard center.
    # It should teleport to (100.0, 100.0), take 10 damage, and get cooldown.
    assert b2.x == 100.0
    assert b2.y == 100.0
    assert b2.hp == 90.0
    assert b2.graveyard_teleport_cd == 2.0

    # Tick 3: B2 cooldown goes down.
    mode.tick(world, balls, 0.5)
    assert b2.graveyard_teleport_cd == 1.5

    # Tick 4: B2 cooldown still active, even if in hazard again, shouldn't teleport.
    b2.x = 500.0
    b2.y = 500.0
    mode.tick(world, balls, 0.016)
    assert b2.x == 500.0
    assert b2.y == 500.0
