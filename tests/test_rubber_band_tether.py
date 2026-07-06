import pytest
from ai.game_modes import RubberBandTetherMode

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100
        self.vx = 0
        self.vy = 0
        self.radius = 10.0
        self.ball_type = "player"
        self.damage = 10.0

class MockWorld:
    def __init__(self):
        self.events = []
        self.dead_balls = []

    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage

def test_rubber_band_tether_setup():
    mode = RubberBandTetherMode()
    world = MockWorld()
    b1 = MockBall(1, 0, 0, "A")
    b2 = MockBall(2, 10, 0, "A")
    b3 = MockBall(3, 0, 10, "B")

    balls = [b1, b2, b3]
    mode.setup(world, balls)

    # Team A balls should be tethered
    assert getattr(b1, "tether_target", None) == b2
    assert getattr(b2, "tether_target", None) == b1
    # Team B ball should not be tethered
    assert getattr(b3, "tether_target", None) is None

def test_rubber_band_tether_snap_and_damage():
    mode = RubberBandTetherMode()
    mode.max_distance = 100.0
    mode.snap_force = 10.0
    mode.snap_damage = 50.0

    world = MockWorld()

    b1 = MockBall(1, 0, 0, "A")
    b2 = MockBall(2, 200, 0, "A") # Further than max_distance (200 > 100)
    b3 = MockBall(3, 100, 0, "B") # In between b1 and b2

    # Setup tether targets directly for focused test
    b1.tether_target = b2
    b2.tether_target = b1

    balls = [b1, b2, b3]

    mode.tick(world, balls, delta=1.0) # Delta 1.0 for simple calculation

    # Check snap force
    # Snap force is 10 * 60 = 600 applied over 1.0 delta
    # nx for b1 towards b2 is 1.0, so b1.vx increases by 600
    assert b1.vx == 600.0
    # b2 is pulled towards b1 (nx is 1.0, but target gets -nx), so b2.vx is -600
    assert b2.vx == -600.0

    # Check damage on b3
    # Initial hp was 100, b3 should take 50 damage
    assert b3.hp == 50.0
