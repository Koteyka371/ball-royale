import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.hazards = []

class MockBooster:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = [MockBooster(100, 100)]
        self.events = []

    def add_event(self, kind, payload):
        self.events.append((kind, payload))

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15
        self.alive = True
        self.active_pet = None
        self.base_speed = 100
        self.base_damage = 10
        self.speed = 100
        self.damage = 10
        self.biome_modifier_speed = False
        self.biome_modifier_damage = False

def test_pet_taming_mode():
    mode = GAME_MODES["pet_taming"]
    world = MockWorld()
    balls = [MockBall(1, 100, 100)]

    mode.setup(world, balls)

    assert len(mode.wild_pets) == 15

    # Force a pet near the ball
    mode.wild_pets[0].x = 100
    mode.wild_pets[0].y = 100

    mode.tick(world, balls, 0.1)

    # Pet should be tamed
    assert len(mode.wild_pets) == 14
    assert balls[0].active_pet is not None
    assert len(world.events) > 0

    # Test tick effects (stat boosts, follow)
    mode.tick(world, balls, 0.1)

    pet = balls[0].active_pet
    if pet.kind == "speed_pet":
        assert balls[0].speed == 120
    elif pet.kind == "power_pet":
        assert balls[0].damage == 13
    elif pet.kind == "loot_pet":
        assert world.boosters[0].x != 100

    balls[0].x = 200
    balls[0].y = 200
    mode.tick(world, balls, 0.1)
    # Pet should follow
    assert pet.x != 100 or pet.y != 100
