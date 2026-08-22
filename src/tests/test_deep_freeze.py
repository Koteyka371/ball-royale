import pytest
from ai.game_modes import DeepFreezeMutatorMode, GAME_MODES
from arena.procedural_arena import Hazard

def test_deep_freeze_mutator():
    assert 'deep_freeze_mutator' in GAME_MODES
    mode = GAME_MODES['deep_freeze_mutator']
    assert isinstance(mode, DeepFreezeMutatorMode)

    class MockArena:
        def __init__(self):
            self.hazards = [Hazard(id=999, x=100, y=100, radius=30.0, kind='ice_patches', damage=0.0)]
            self.width = 1000
            self.height = 1000

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()
            self.events = []

        def add_event(self, name, data):
            self.events.append((name, data))

    class MockBall:
        def __init__(self, x, y):
            self.id = 1
            self.x = x
            self.y = y
            self.radius = 10.0
            self.alive = True
            self.speed = 100.0
            self.base_speed = 100.0
            self.hp = 100.0
            self.freeze_level = 0.0

        def take_damage(self, amount):
            self.hp -= amount
            if self.hp <= 0:
                self.alive = False

    world = MockWorld()
    balls = [MockBall(200, 200)]

    mode.setup(world, balls)

    # We should have thermal vents and more ice patches now
    vents = [h for h in world.arena.hazards if getattr(h, 'kind', '') == 'thermal_vent']
    ice = [h for h in world.arena.hazards if getattr(h, 'kind', '') == 'ice_patches']
    assert len(vents) >= 5
    assert len(ice) >= 6

    # Put ball far away from any thermal vent
    b = balls[0]
    # Place a vent far away
    vents[0].x = 800
    vents[0].y = 800
    b.x = 100
    b.vx = 0
    b.vy = 0
    b.y = 100
    b.vx = 0
    b.vy = 0

    # Tick loop to simulate freeze
    for _ in range(30): # 15 seconds needed to freeze, tick is delta
        mode.tick(world, balls, delta=0.5)

    assert b.freeze_level >= 0.99
    assert b.speed <= getattr(b, 'base_speed', 100.0) * 0.51 # 0.5 penalty

    # Further ticks should cause damage
    mode.tick(world, balls, delta=1.0)
    assert b.hp == 95.0

    # Put ball next to vent
    b.x = vents[0].x
    b.y = vents[0].y

    # Tick to thaw
    for _ in range(30): # 5 seconds needed to thaw
        mode.tick(world, balls, delta=0.5)

    assert b.freeze_level == 0.0
    import math
    assert math.isclose(b.speed, getattr(b, 'base_speed', 100.0), rel_tol=1e-5)

    # Check ice expansion
    old_r = ice[0].radius
    mode.tick(world, balls, delta=1.0)
    assert ice[0].radius > old_r
