import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.radius = 15.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "player"
    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

def test_quadrant_royale_mode():
    mode = GAME_MODES["quadrant_royale"]
    world = MockWorld()

    b1 = MockBall(1, 250.0, 250.0)
    b2 = MockBall(2, 450.0, 450.0)

    mode.setup(world, [b1, b2])

    initial_b1_hp = b1.hp
    initial_b2_hp = b2.hp

    mode.tick(world, [b1, b2], 1.0)

    assert b1.hp == initial_b1_hp
    assert b2.hp < initial_b2_hp

    mode.tick(world, [b1, b2], 10.0)

    assert len(mode.portals) >= 2
    assert any(e[0] == "portal_spawned" for e in world.events)

    portal = mode.portals[0]
    b1.x = portal["x"]
    b1.y = portal["y"]
    portal["cooldown"] = 0.0

    world.events = []
    mode.tick(world, [b1], 0.1)

    # We added an offset logic earlier so check with a margin
    assert abs(b1.x - portal["target_x"]) <= 15.0
    assert abs(b1.y - portal["target_y"]) <= 15.0
    assert any(e[0] == "teleported" for e in world.events)
