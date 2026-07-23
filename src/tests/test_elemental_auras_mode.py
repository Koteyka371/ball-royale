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
        self.base_speed = 100.0
        self.speed = 100.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.elemental_auras = {"fire": 0, "water": 0, "earth": 0, "lightning": 0}

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

def test_elemental_auras_mode_crafting_station():
    mode = ElementalAurasMode()
    world = MockWorld()

    b1 = MockBall(1, 500, 500, "A")
    b2 = MockBall(2, 600, 600, "B")

    mode.setup(world, [b1, b2])

    class MockHazard:
        def __init__(self, kind, x, y):
            self.kind = kind
            self.x = x
            self.y = y
            self.radius = 40.0
            self.active = True

    # Test collecting an aura from a crafting station
    world.arena.hazards.append(MockHazard("crafting_station_water", 500, 500))
    mode.tick(world, [b1, b2], 0.016)

    assert b1.elemental_auras.get("water", 0) == 1
    assert len(world.arena.hazards) == 0  # Consumed

    # Test depositing an aura for a hybrid effect (Fire + Water)
    b1.elemental_auras["fire"] = 1
    world.arena.hazards.append(MockHazard("crafting_station_water", 500, 500))

    # Fast forward so crafting station can be interacted with
    mode.tick(world, [b1, b2], 0.016)

    assert b1.elemental_auras.get("fire", 0) == 0  # Deposited
    assert b1.speed > 100.0  # Speed boost triggered
    assert len(world.arena.hazards) == 0
    assert len(world.events) == 1
    assert world.events[0][0] == "hybrid_crafted"
    assert "fire" in world.events[0][1]["elements"]
    assert "water" in world.events[0][1]["elements"]
