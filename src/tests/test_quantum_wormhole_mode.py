import pytest
from ai.game_modes import GAME_MODES, QuantumWormholeMode

class DummyArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = [DummyHazard(150.0, 500.0)]

class DummyHazard:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10.0

class DummyProjectile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5.0
        self.alive = True

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.events = []
        self.projectiles = [DummyProjectile(150.0, 500.0)]

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class DummyBall:
    def __init__(self, x, y):
        self.id = 1
        self.x = x
        self.y = y
        self.alive = True
        self.radius = 10.0
        self.vx = 50.0
        self.vy = 20.0

def test_quantum_wormhole_mode():
    mode = GAME_MODES.get("quantum_wormhole")
    assert isinstance(mode, QuantumWormholeMode)

    world = DummyWorld()
    # Ball inside the first wormhole zone (x=150, y=500)
    b = DummyBall(150.0, 500.0)
    balls = [b]

    # Run the setup manually or let tick handle it
    mode.setup(world, balls)

    # Tick should trigger teleportation
    orig_vx = b.vx
    orig_vy = b.vy

    mode.tick(world, balls, delta=0.01)

    assert mode.setup_done

    linked_x = 1000.0 - 150.0
    linked_y = 500.0

    # Ball should have teleported
    assert b.x == linked_x
    assert b.y == linked_y
    # Ball should retain velocity exactly
    assert b.vx == orig_vx
    assert b.vy == orig_vy

    # Hazard should have teleported
    h = world.arena.hazards[0]
    assert h.x == linked_x
    assert h.y == linked_y

    # Projectile should have teleported
    p = world.projectiles[0]
    assert p.x == linked_x
    assert p.y == linked_y
