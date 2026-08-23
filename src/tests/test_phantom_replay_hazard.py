import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []
        self.events = []

class MockEntity:
    def __init__(self, e_id, x, y, alive=True, hp=100.0, radius=15.0):
        self.id = e_id
        self.x = x
        self.y = y
        self.alive = alive
        self.hp = hp
        self.radius = radius

def test_projectile_replay_hazard_logic():
    mode = GAME_MODES["phantom_replay_hazard"]
    world = MockWorld()

    ball = MockEntity(1, 500, 500)
    mode.setup(world, [ball])

    assert mode.phase == "record"

    # Add a projectile inside the hazard
    # hazard is at 500, 500, radius 200
    projectile = MockEntity(99, 500, 500)
    world.projectiles.append(projectile)

    # Tick during record phase
    mode.tick(world, [ball], 1.0)

    assert 99 in mode.recordings
    assert len(mode.recordings[99]) == 1

    # Tick past record duration (3.0)
    mode.tick(world, [ball], 2.5)

    assert mode.phase == "delay"

    # Tick past delay duration (1.0)
    mode.tick(world, [ball], 1.5)

    assert mode.phase == "replay"
    assert len(mode.phantoms) == 1

    phantom = mode.phantoms[0]
    assert phantom.alive

    # Tick during replay phase (phantom should deal damage to ball overlapping it)
    initial_hp = ball.hp
    mode.tick(world, [ball], 1.0)

    assert ball.hp < initial_hp

    # Tick past replay duration (15.0)
    mode.tick(world, [ball], 15.0)

    assert mode.phase == "cooldown"
    assert len(mode.phantoms) == 0
