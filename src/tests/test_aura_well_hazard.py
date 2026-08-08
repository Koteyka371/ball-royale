import pytest
from ai.game_modes import AuraWellHazardMode

class MockBall:
    def __init__(self, id, team, aura_color, x, y):
        self.id = id
        self.team = team
        self.aura_color = aura_color
        self.x = x
        self.y = y
        self.radius = 20.0
        self.alive = True
        self.hp = 50.0
        self.max_hp = 100.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self.aura_well_buff_timer = 0.0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class MockHazard:
    def __init__(self, id, x, y):
        self.id = id
        self.kind = "aura_well"
        self.active = True
        self.x = x
        self.y = y
        self.radius = 60.0
        self.absorbed_aura = None
        self.pulse_timer = 0.0
        self.pulse_interval = 3.0
        self.pulse_radius = 250.0

class MockArena:
    def __init__(self):
        self.width = 2000.0
        self.height = 2000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

def test_aura_well_absorbs_and_pulses():
    mode = AuraWellHazardMode()
    world = MockWorld()

    # We will test tick directly on an empty world with our mock hazard
    h = MockHazard(1, 1000.0, 1000.0)
    world.arena.hazards.append(h)

    b1 = MockBall(1, "team1", "blue", 1000.0, 1050.0)  # Inside hazard radius
    b2 = MockBall(2, "team2", "red", 1000.0, 1150.0)   # Outside hazard radius but inside pulse radius
    balls = [b1, b2]

    mode.tick(world, balls, 0.016)

    assert h.absorbed_aura == "blue"

    # Now simulate pulse
    h.pulse_timer = 0.0
    mode.tick(world, balls, 0.016)

    assert b1.hp == 70.0 # Healed
    assert b1.aura_well_buff_timer == 3.0 # Buffed

    assert b2.hp == 30.0 # Damaged
    assert b2.aura_well_buff_timer == 0.0 # Not buffed
