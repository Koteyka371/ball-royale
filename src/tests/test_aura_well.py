import pytest
from ai.game_modes import AuraWellHazardMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, id, x, y, aura_color):
        self.id = id
        self.x = x
        self.y = y
        self.aura_color = aura_color
        self.team = f"Aura {aura_color}"
        self.radius = 20.0
        self.alive = True
        self.hp = 50.0
        self.max_hp = 100.0

def test_aura_well_hazard():
    mode = AuraWellHazardMode()
    world = MockWorld()

    # We don't want setup to spawn random ones, we can just clear and add our own
    mode.setup(world, [])
    world.arena.hazards.clear()

    class Hazard:
        def __init__(self, id, x, y, radius, kind, damage):
            self.id = id; self.x = x; self.y = y; self.radius = radius; self.kind = kind; self.damage = damage
            self.active = True

    well = Hazard(1, 100.0, 100.0, 60.0, "aura_well", 0.0)
    setattr(well, "absorbed_aura", None)
    setattr(well, "pulse_timer", 0.0)
    setattr(well, "pulse_interval", 3.0)
    setattr(well, "pulse_radius", 250.0)

    world.arena.hazards.append(well)

    b1 = MockBall(1, 100.0, 100.0, "Red")
    b2 = MockBall(2, 200.0, 200.0, "Red") # In pulse radius (dist ~141)
    b3 = MockBall(3, 100.0, 200.0, "Blue") # In pulse radius (dist 100)

    # Tick 1: b1 charges the well
    mode.tick(world, [b1, b2, b3], delta=0.016)

    assert well.absorbed_aura == "Red"

    # Tick 2: timer is 0 initially, wait, the timer shouldn't pulse on the exact frame it charges?
    # Ah, in my code, if it wasn't charged, it charges it. It doesn't pulse in the same tick.
    # Next tick, pulse_timer is 0, so it will pulse!
    mode.tick(world, [b1, b2, b3], delta=0.016)

    # pulse timer should be set to 3.0
    assert getattr(well, "pulse_timer", 0.0) > 2.9

    # b1 and b2 should be healed
    assert b1.hp == 70.0
    assert b2.hp == 70.0

    # b3 should be damaged
    assert b3.hp == 30.0
