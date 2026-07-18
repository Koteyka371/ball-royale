from ai.game_modes import MutantSafeZoneMode

class MockEntity:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "basic"
        self.hp = 100.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage_multiplier = 1.0
        self.damage_multiplier = 1.0
        self.base_perception_radius = 250.0
        self.perception_radius = 250.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_mutant_safe_zone_inside():
    mode = MutantSafeZoneMode()
    world = MockWorld()
    b = MockEntity(1, 500, 500)
    mode.setup(world, [b])

    initial_speed = b.base_speed
    mode.tick(world, [b], 1.0)

    assert b.base_speed == initial_speed

def test_mutant_safe_zone_outside():
    import random
    random.seed(42) # Seed to guarantee mutations happen and don't match initial exactly
    mode = MutantSafeZoneMode()
    world = MockWorld()
    b = MockEntity(1, 10, 10) # Far outside
    mode.setup(world, [b])

    initial_speed = b.base_speed
    initial_dmg = b.base_damage_multiplier
    initial_perc = b.base_perception_radius

    for _ in range(50):
        mode.tick(world, [b], 0.1)

    assert b.base_speed != initial_speed or b.base_damage_multiplier != initial_dmg or b.base_perception_radius != initial_perc
