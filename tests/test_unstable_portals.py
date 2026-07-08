import pytest
from ai.game_modes import UnstablePortalsEventMode

class DummyWorld:
    def __init__(self):
        self.events = []
        self.arena = type('Arena', (), {'width': 800, 'height': 600})()

    def add_event(self, kind, data):
        self.events.append((kind, data))

class DummyBall:
    def __init__(self, x, y, id=1):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100
        self.radius = 10
        self.damage_taken = 0

    def take_damage(self, amount):
        self.hp -= amount
        self.damage_taken += amount

def test_unstable_portals():
    mode = UnstablePortalsEventMode()
    world = DummyWorld()
    balls = [DummyBall(150, 150)]

    # Tick to spawn a portal
    for _ in range(100):
        mode.tick(world, balls, delta=1.0)
        if mode.portals:
            break

    assert len(mode.portals) > 0

    portal = mode.portals[0]
    px, py = portal["x"], portal["y"]

    # Move ball near the portal
    balls[0].x = px + 10
    balls[0].y = py + 10

    # Wait for collapse
    for _ in range(200):
        mode.tick(world, balls, delta=0.1)
        if not mode.portals:
            break

    assert len(mode.portals) == 0
    assert balls[0].damage_taken > 0
    # # assert "explosion" in [e[0] for e in world.events]
    assert "portal_blast" in [e[0] for e in world.events]
