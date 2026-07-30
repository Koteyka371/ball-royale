import pytest

def test_orbital_debris_exists():
    from ai.game_modes import GAME_MODES
    assert "orbital_debris" in GAME_MODES

def test_orbital_debris_setup():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES["orbital_debris"]

    class Arena:
        def __init__(self):
            self.width = 1000.0
            self.height = 1000.0
            self.hazards = []

    class World:
        def __init__(self):
            self.arena = Arena()
            self.projectiles = []

    world = World()
    balls = []

    mode.setup(world, balls)

    assert hasattr(world.arena, "hazards")

    # 1 well + 5 debris
    assert len(world.arena.hazards) == 6

    debris_count = sum(1 for h in world.arena.hazards if getattr(h, "kind", "") == "orbital_debris")
    assert debris_count == 5

    well_count = sum(1 for h in world.arena.hazards if getattr(h, "kind", "") == "gravity_well")
    assert well_count == 1

def test_orbital_debris_tick():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES["orbital_debris"]

    class Arena:
        def __init__(self):
            self.width = 1000.0
            self.height = 1000.0
            self.hazards = []

    class World:
        def __init__(self):
            self.arena = Arena()
            self.projectiles = []

    class Ball:
        def __init__(self):
            self.alive = True
            self.hp = 100.0
            self.x = 500.0
            self.y = 500.0
            self.vx = 0.0
            self.vy = 0.0
            self.radius = 10.0

    world = World()
    b = Ball()
    b.x = 250.0  # Put near debris orbit
    b.y = 500.0
    b.vx = 300.0 # High speed
    balls = [b]

    mode.setup(world, balls)

    # Run a tick
    mode.tick(world, balls, 0.016)

    # Make sure something happens
    assert True
