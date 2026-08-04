import pytest
from ai.game_modes import SolarFlareMode

class MockWorld:
    def __init__(self):
        self.solar_flare_active = False
        self.arena = self.MockArena()
        self.events = []

    def add_event(self, t, d):
        self.events.append((t, d))

    class MockArena:
        def __init__(self):
            self.hazards = []
            self.width = 1000
            self.height = 1000

class MockHazard:
    def __init__(self, kind, x, y, width=50, height=50, radius=50):
        self.kind = kind
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = radius
        self.is_disabled_by_flare = False

class MockBall:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.shield_active = True
        self.has_aegis_shield = True
        self.electronic_items_disabled = False
        self.perception_radius = 250.0

def test_solar_flare_damage_and_disable():
    mode = SolarFlareMode()
    world = MockWorld()
    b1 = MockBall(0, 0)
    b2 = MockBall(500, 500)

    # b2 is in shade (behind indestructible wall)
    world.arena.hazards.append(MockHazard("indestructible_wall", 500-100, 500-100, width=50, height=50))
    # b3 is in shade (shadow)
    b3 = MockBall(800, 800)
    world.arena.hazards.append(MockHazard("meteor_shadow", 800, 800, radius=20))

    # wait for flare
    mode.tick(world, [b1, b2, b3], delta=20.0)
    assert world.solar_flare_active

    # Tick inside flare
    mode.tick(world, [b1, b2, b3], delta=1.0)

    # b1 is outside shade, takes damage
    assert b1.hp < 100.0

    # b2 is behind indestructible_wall
    # wall dx = b2.x - w.x = 500 - 400 = 100
    # dy = b2.y - w.y = 500 - 400 = 100
    # dot = 100*0.707 + 100*0.707 = 141.4
    # perp_dist = abs(100*-0.707 + 100*0.707) = 0
    # In shade!
    assert b2.hp == 100.0

    # b3 is in shadow
    assert b3.hp == 100.0

    # All should have electronics disabled
    assert b1.electronic_items_disabled == True
    assert b2.electronic_items_disabled == True
    assert b3.electronic_items_disabled == True
    assert b1.shield_active == False
    assert b2.shield_active == False

    # End flare
    mode.tick(world, [b1, b2, b3], delta=5.0)
    assert world.solar_flare_active == False
    assert b1.electronic_items_disabled == False
    assert b2.electronic_items_disabled == False
