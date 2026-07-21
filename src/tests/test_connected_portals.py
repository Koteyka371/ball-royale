import pytest
from ai.game_modes import ConnectedPortalsMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []
        self.weather = "clear"
        self.temperature = 20.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []
        self.events = []
        self.mutators = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y, radius=20):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.alive = True
        self.portal_cooldown = 0.0
        self.team = "A"

class MockProjectile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.teleport_cooldown = 0.0

def test_connected_portals_mode():
    mode = ConnectedPortalsMode()
    world = MockWorld()
    balls = [MockBall("b1", 500, 500)]

    # Force portal spawn
    mode.spawn_timer = 0
    mode.tick(world, balls, 0.016)

    assert len(mode.portals) == 4 # 2 pairs
    assert len(world.arena.hazards) == 4

    p1 = mode.portals[0]
    p2_id = p1["target_id"]
    p2 = next(p for p in mode.portals if p["id"] == p2_id)

    # Teleport a ball
    balls[0].x = p1["x"]
    balls[0].y = p1["y"]

    mode.tick(world, balls, 0.016)

    # Check if ball moved to p2
    assert balls[0].x == p2["x"]
    assert balls[0].y == p2["y"]
    assert balls[0].portal_cooldown > 0

    # Check cooldown prevents instant teleport back
    mode.tick(world, balls, 0.016)
    assert balls[0].x == p2["x"]
    assert balls[0].y == p2["y"]

    # Test projectile teleport
    proj = MockProjectile(p1["x"], p1["y"])
    world.projectiles.append(proj)

    mode.tick(world, balls, 0.016)

    assert proj.x == p2["x"]
    assert proj.y == p2["y"]
    assert proj.teleport_cooldown > 0

    # Test projectile cooldown
    mode.tick(world, balls, 0.016)
    assert proj.x == p2["x"]
    assert proj.y == p2["y"]
