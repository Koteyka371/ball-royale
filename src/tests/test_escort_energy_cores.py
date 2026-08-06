import pytest
from ai.game_modes import EscortMode

class MockWorld:
    def __init__(self):
        self.events = []
        self.dead_balls = []
        self.arena = MockArena()

    def add_event(self, type, data):
        self.events.append((type, data))

class MockArena:
    def __init__(self):
        self.hazards = []
        self.weather = "clear"

class MockBall:
    def __init__(self, id):
        self.id = id
        self.ball_type = "basic"
        self.alive = True
        self.team = "Attackers"
        self.x = 500.0
        self.y = 500.0
        self.radius = 15.0
        self.has_energy_core = False

def test_escort_mode_energy_cores():
    mode = EscortMode()
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    b3 = MockBall(3)

    mode.setup(world, [b1, b2, b3])
    payload = mode.payload
    payload.x = 500.0
    payload.y = 500.0
    mode.energy_core_spawn_timer = 7.99

    mode.tick(world, [b1, b2, b3], delta=0.02)

    core = next(h for h in world.arena.hazards if h.kind == "energy_core")

    b2.x = core.x
    b2.y = core.y
    b2.has_energy_core = False
    mode.tick(world, [b1, b2, b3], delta=0.02)
    assert b2.has_energy_core == True

    b2.x = payload.x
    b2.y = payload.y
    mode.tick(world, [b1, b2, b3], delta=0.02)
    assert getattr(payload, "energy_cores", 0) == 1

    b3.has_energy_core = True
    b3.x = payload.x
    b3.y = payload.y
    mode.tick(world, [b1, b2, b3], delta=0.02)
    assert payload.energy_cores == 2

    b2.has_energy_core = True
    payload.shield = 0.0 # reset before 3rd deposit
    mode.tick(world, [b1, b2, b3], delta=0.02)

    assert payload.energy_cores == 0
    assert payload.overcharge_timer == 5.0
    assert payload.shield == 100.0
