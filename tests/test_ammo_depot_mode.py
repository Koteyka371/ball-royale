import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.radius = 20.0
        self.alive = True
        self.base_damage = 10.0
        self.attack_speed = 1.0

class MockArena:
    def __init__(self):
        self.width = 2000
        self.height = 2000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_ammo_depot_setup():
    mode = GAME_MODES["ammo_depot"]
    world = MockWorld()
    b = MockBall(1, 100, 100)

    mode.setup(world, [b])
    mode.ammo_spawn_timer = 2.0
    assert b.ammo_buff_timer == 0.0
    assert abs(b.base_damage - 1.0) < 0.001
    assert abs(b.attack_speed - 0.1) < 0.001

def test_ammo_depot_spawn_ammo():
    mode = GAME_MODES["ammo_depot"]
    world = MockWorld()
    b = MockBall(1, 100, 100)
    mode.setup(world, [b])
    mode.ammo_spawn_timer = 2.0

    # Tick with large delta to trigger ammo spawn
    mode.tick(world, [b], 2.1)

    assert len(world.boosters) == 1
    assert world.boosters[0].kind == "ammo_pack"
    assert world.boosters[0].active == True

def test_ammo_depot_pickup():
    mode = GAME_MODES["ammo_depot"]
    world = MockWorld()
    b = MockBall(1, 100, 100)
    mode.setup(world, [b])
    mode.ammo_spawn_timer = 2.0

    # Force spawn ammo
    mode.tick(world, [b], 2.1)
    ammo = world.boosters[0]

    # Move ball to ammo
    b.x = ammo.x
    b.y = ammo.y

    # Tick to process collision
    mode.tick(world, [b], 0.016)
    mode.tick(world, [b], 0.016) # extra tick for timer processing

    # Check buff applied
    assert ammo.active == False
    assert b.ammo_buff_timer > 0.0
    assert b.base_damage > 10.0
    assert b.attack_speed > 1.0

    # Tick until buff expires
    mode.tick(world, [b], 5.0)
    assert b.ammo_buff_timer == 0.0
    assert abs(b.base_damage - 1.0) < 0.001
    assert abs(b.attack_speed - 0.1) < 0.001
