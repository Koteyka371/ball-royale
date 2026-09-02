import pytest
from unittest.mock import MagicMock
from ai.random_portals import RandomPortalsMode

class DummyWorld:
    def __init__(self):
        self.arena = MagicMock()
        self.arena.width = 1000
        self.arena.height = 1000
        self.events = []
        self.projectiles = []

    def add_event(self, type, data):
        self.events.append((type, data))

class DummyProjectile:
    def __init__(self, x, y, radius, vx, vy):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = vx
        self.vy = vy
        self.alive = True
        self.active = True
        self.is_projectile = True

def test_random_portals_teleports_projectiles():
    mode = RandomPortalsMode()
    world = DummyWorld()

    # Initialize the portals
    mode.setup(world, [])

    # Setup portals manually to test
    mode.portals = [
        {"x": 100, "y": 100, "radius": 50, "cooldown": 0},
        {"x": 800, "y": 800, "radius": 50, "cooldown": 0}
    ]

    # Create a projectile just entering the first portal
    proj = DummyProjectile(100, 100, 10, 100, 0)
    world.projectiles.append(proj)

    # Tick the mode
    mode.tick(world, [], delta=0.1)

    # Check if the projectile was teleported to the other portal
    # The new position should be around 800, 800
    assert proj.x > 700 and proj.x < 900
    assert proj.y > 700 and proj.y < 900
    assert proj.vx == 100
    assert proj.vy == 0
