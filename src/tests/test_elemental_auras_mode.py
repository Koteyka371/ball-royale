import pytest
from ai.game_modes import ElementalAurasMode

class MockBall:
    def __init__(self, id, x, y, team="A"):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15.0
        self.team = team
        self.alive = True
        self.ball_type = "player"

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, name, data):
        self.events.append([name, data])

def test_elemental_auras_mode_disruption():
    mode = ElementalAurasMode()
    world = MockWorld()

    b1 = MockBall(1, 500, 500, "A")
    b2 = MockBall(2, 600, 600, "B")

    mode.setup(world, [b1, b2])

    b2.elemental_auras["fire"] = 1

    class MockHazard:
        def __init__(self, kind, x, y):
            self.kind = kind
            self.x = x
            self.y = y
            self.radius = 20.0
            self.active = True

    world.arena.hazards.append(MockHazard("aura_pickup_water", 500, 500))

    mode.tick(world, [b1, b2], 0.016)

    assert b1.elemental_auras.get("water", 0) == 1
    assert b2.elemental_auras.get("fire", 0) == 0
    assert len(world.events) == 1
    assert world.events[0][0] == "aura_disrupted"
    assert world.events[0][1]["id"] == 2
    assert world.events[0][1]["element"] == "fire"
