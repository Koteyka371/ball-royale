import pytest
from src.ai.game_modes import SiphonBeamMode

class MockBall:
    def __init__(self, id, x, y, hp=100.0, team="red", score=0):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100.0
        self.team = team
        self.score = score
        self.alive = True
        self.ball_type = "normal"
        self.stamina = 100.0
        self.base_speed_multiplier = 1.0
        self.speed_multiplier = 1.0
        self.orbital_link_timer = 0.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

    def clamp_position(self, x, y, radius):
        return x, y, False

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.next_id = 1
        self.events = []

    def add_event(self, event_name, data):
        self.events.append((event_name, data))

def test_siphon_beam_mode_heals_caller():
    world = MockWorld()
    # Ball 1 is far, full hp. Ball 2 is close, low hp (caller). Ball 3 is target.
    b1 = MockBall(1, 100, 100, hp=100.0, score=10)
    b2 = MockBall(2, 200, 200, hp=50.0, score=5) # lowest hp
    b3 = MockBall(3, 500, 500, hp=100.0, score=100) # highest score -> target

    mode = SiphonBeamMode()
    mode.setup(world, [b1, b2, b3])

    # Tick past spawn
    mode.tick(world, [b1, b2, b3], delta=3.1)

    assert len(mode.crosshairs) == 1
    ch = mode.crosshairs[0]
    assert ch["target_id"] == 3
    assert ch["caller_id"] == 2

    # Manually move target into crosshair and lock on
    ch["x"] = b3.x
    ch["y"] = b3.y
    mode.tick(world, [b1, b2, b3], delta=2.1)

    assert ch["state"] == "locking"

    # Tick past lock on
    mode.tick(world, [b1, b2, b3], delta=3.1)

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "siphon_zone"
    assert getattr(hazard, "caller_id") == 2

    b3_hp_initial = b3.hp
    b2_hp_initial = b2.hp

    # Tick while hazard is active, b3 should take damage, b2 should heal
    mode.tick(world, [b1, b2, b3], delta=1.0)

    assert b3.hp < b3_hp_initial
    assert b2.hp > b2_hp_initial
    assert b1.hp == 100.0

def test_siphon_beam_heals_lowest_hp_if_caller_dead():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, hp=90.0, score=10)
    b2 = MockBall(2, 200, 200, hp=50.0, score=5) # lowest hp
    b3 = MockBall(3, 500, 500, hp=100.0, score=100)

    mode = SiphonBeamMode()
    mode.setup(world, [b1, b2, b3])

    # Manually insert hazard with dead caller
    class SiphonHazard:
        def __init__(self, x, y, caller_id):
            self.id = 1
            self.x = x
            self.y = y
            self.radius = 80.0
            self.kind = "siphon_zone"
            self.damage = 0.0
            self.active = True
            self.duration = 15.0
            self.caller_id = caller_id

    h = SiphonHazard(b3.x, b3.y, 999) # 999 is dead/non-existent
    world.arena.hazards.append(h)

    b3_hp_initial = b3.hp
    b2_hp_initial = b2.hp

    mode.tick(world, [b1, b2, b3], delta=1.0)

    assert b3.hp < b3_hp_initial
    assert b2.hp > b2_hp_initial
