import pytest
from ai.idea_2_gravity_pulse_mine import GravityPulseMineMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockEntity:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.team = team
        self.alive = True

def test_gravity_pulse_mine_spawn():
    mode = GravityPulseMineMode()
    world = MockWorld()
    balls = [MockEntity(100, 100, "red")]

    # Tick past spawn interval
    mode.tick(world, balls, delta=16.0)

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "idea_2_gravity_pulse_mine"
    assert hazard.team == "red"

def test_gravity_pulse_mine_effect():
    mode = GravityPulseMineMode()
    world = MockWorld()

    class MockHazard:
        def __init__(self):
            self.x = 500.0
            self.y = 500.0
            self.kind = "idea_2_gravity_pulse_mine"
            self.active = True
            self.duration = 10.0
            self.team = "blue"
            self.pulse_timer = 1.9
            self.pulse_interval = 2.0
            self.pulse_radius = 250.0

    hazard = MockHazard()
    world.arena.hazards.append(hazard)

    # One ally, one enemy inside radius
    ally = MockEntity(500, 400, "blue") # Above the mine (dx=0, dy=-100)
    enemy = MockEntity(500, 400, "red") # Above the mine (dx=0, dy=-100)

    balls = [ally, enemy]

    # Tick to trigger pulse
    mode.tick(world, balls, delta=0.2)

    # Ally should be pulled (dy is negative, pulling means increasing vy)
    # Actually: dy = b.y - h.y = 400 - 500 = -100
    # ny = -100 / 100 = -1
    # ally pulls: b.vy -= ny * 200 = -(-1) * 200 = +200 -> positive vy
    assert ally.vy > 0.0

    # Enemy should be pushed (dy is negative, ny = -1)
    # enemy pushes: b.vy += ny * 200 = -1 * 200 = -200 -> negative vy
    assert enemy.vy < 0.0

def test_gravity_pulse_mine_duration():
    mode = GravityPulseMineMode()
    world = MockWorld()

    class MockHazard:
        def __init__(self):
            self.x = 500.0
            self.y = 500.0
            self.kind = "idea_2_gravity_pulse_mine"
            self.active = True
            self.duration = 0.01
            self.team = "blue"
            self.pulse_timer = 0.0
            self.pulse_interval = 2.0
            self.pulse_radius = 250.0

    hazard = MockHazard()
    world.arena.hazards.append(hazard)

    mode.tick(world, [], delta=0.1)

    # Hazard should be deactivated and removed
    assert len(world.arena.hazards) == 0
    assert hazard.active == False
