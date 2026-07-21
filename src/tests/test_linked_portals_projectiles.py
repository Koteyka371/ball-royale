class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.projectiles = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, x, y):
        self.id = id(self)
        self.x = x
        self.y = y
        self.radius = 10
        self.alive = True

class MockProjectile:
    def __init__(self, x, y):
        self.id = id(self)
        self.x = x
        self.y = y
        self.radius = 5
        self.alive = True

from ai.game_modes import LinkedPortalsMode

def test_linked_portals_projectiles():
    world = MockWorld()
    mode = LinkedPortalsMode()
    balls = []
    mode.setup(world, balls)

    # Fast forward to spawn portals
    for _ in range(600):
        mode.tick(world, balls, 0.01)

    assert len(mode.portals) == 2

    p1 = mode.portals[0]
    p2 = mode.portals[1]

    # Test projectile teleportation
    proj = MockProjectile(p1["x"], p1["y"])
    world.projectiles.append(proj)

    # Move the tick
    mode.tick(world, balls, 0.01)

    # Check if projectile was teleported
    assert proj.x == p2["x"]
    assert proj.y == p2["y"]
