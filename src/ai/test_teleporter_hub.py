import pytest
from ai.game_modes import TeleporterHubMode

class DummyWorld:
    def __init__(self):
        self.events = []
        self.arena = type('Arena', (), {'width': 800, 'height': 600, 'hazards': []})()

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

def test_teleporter_hub():
    mode = TeleporterHubMode()
    world = DummyWorld()
    balls = [DummyBall(150, 150)]

    mode.setup(world, balls)

    assert len(world.arena.hazards) > 0
    assert len(mode.portals) > 0

    # Tick past shift timer
    for _ in range(600):
        mode.tick(world, balls, delta=0.016)

    assert "portal_shift" in [e[0] for e in world.events]
