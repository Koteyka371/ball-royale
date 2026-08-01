import pytest
from ai.signal_scrambler_mode import SignalScramblerMode
from ai.game_modes import GameMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.alive = True
        self.perception_radius = 250.0

class MockHazard:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10.0
        self.damage = 10.0
        self.vx = 0.0
        self.vy = 0.0

def test_signal_scrambler_mode():
    world = MockWorld()
    balls = [MockBall(1, 500, 500), MockBall(2, 100, 100)]

    mode = SignalScramblerMode()
    mode.setup(world, balls)

    # Tick should spawn the jammer hazard and scramble ball 1
    mode.tick(world, balls, 0.1)
    mode.tick(world, balls, 0.1)

    scramblers = [h for h in world.arena.hazards if getattr(h, "kind", "") == "signal_scrambler"]
    assert len(scramblers) == 1
    assert scramblers[0].x == 500.0
    assert scramblers[0].y == 500.0

    # Ball 1 is at 500,500 (inside 400 radius). Perception should drop to 30.0
    assert balls[0].perception_radius == 30.0
    # Ball 2 is at 100,100 (dist 565 > 400). Perception should stay 250.0
    assert balls[1].perception_radius == 250.0

    # Add a homing missile inside the field
    hm = MockHazard("homing_missile", 510, 500)
    hm.owner_id = -1
    world.arena.hazards.append(hm)

    mode.tick(world, balls, 0.1)

    assert hasattr(hm, "scramble_angle")
    # Because of random scrambling, vx and vy should be set
    assert abs(hm.vx) > 0 or abs(hm.vy) > 0
