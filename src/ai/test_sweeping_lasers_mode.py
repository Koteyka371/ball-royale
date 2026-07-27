import pytest
from ai.game_modes import SweepingLasersMode
from ai.action import Action
import math

class MockHazard:
    def __init__(self, hid, x, y, radius, kind):
        self.id = hid
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick_count = 0

class MockBall:
    def __init__(self):
        self.id = id(self)
        self.alive = True
        self.x = 0.0
        self.y = 0.0
        self.radius = 25.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.speed_multiplier = 1.0
        self.sweeping_laser_cd = 0.0

    def take_damage(self, dmg):
        self.hp -= dmg

def test_sweeping_lasers_mode():
    mode = SweepingLasersMode()
    world = MockWorld()

    ball = MockBall()
    world.balls = [ball]

    mode.setup(world, world.balls)

    assert len(world.arena.hazards) == 1
    laser = world.arena.hazards[0]
    assert laser.kind == "sweeping_laser"

    # Evaluate sweep timer to see where laser goes
    # Initially sweep_timer is 0, then increments by delta=0.5
    # new_sweep_timer = 0.5
    # h.x = center_x + math.sin(0.5 * 2.0) * (arena_width / 2.0 - 150.0)
    # math.sin(1.0) * 350 = 0.84147098 * 350 = 294.51
    # center_x = 500
    # h.x = 794.51

    # Place ball exactly where the laser will be after delta
    ball.x = 794.51
    ball.y = 50.0

    mode.tick(world, world.balls, delta=0.5)

    assert ball.sweeping_laser_cd == 1.0
    assert ball.radius == pytest.approx(25.0 * 0.9)
    assert ball.max_hp == pytest.approx(100.0 * 0.9)
    assert ball.hp == pytest.approx(50.0)
    assert ball.speed_multiplier == pytest.approx(1.0 * 1.2)

    # Tick again immediately, should take damage but NOT shrink again
    prev_hp = ball.hp
    prev_radius = ball.radius
    prev_max_hp = ball.max_hp
    prev_speed = ball.speed_multiplier

    mode.tick(world, world.balls, delta=0.5)
    assert ball.hp < prev_hp
    assert ball.sweeping_laser_cd == pytest.approx(0.5)
    assert ball.radius == pytest.approx(prev_radius)
    assert ball.max_hp == pytest.approx(prev_max_hp)
    assert ball.speed_multiplier == pytest.approx(prev_speed)

    # Wait for cooldown to expire
    mode.tick(world, world.balls, delta=0.51)
    # CD goes below 0, should take effect again next tick
    assert ball.sweeping_laser_cd <= 0.0

    # Move ball out of way temporarily to prevent continuous damage killing it before next tick
    ball.x = 0.0

    # Tick with no collision
    mode.tick(world, world.balls, delta=0.5)
    assert ball.sweeping_laser_cd <= 0.0

    # Move ball back to laser (laser moves but we force ball to be there)
    ball.x = laser.x

    # Now it hits and CD is <= 0, so it triggers again
    mode.tick(world, world.balls, delta=0.1)

    assert ball.sweeping_laser_cd == 1.0
    assert ball.radius == pytest.approx(prev_radius * 0.9)
    assert ball.max_hp == pytest.approx(prev_max_hp * 0.9)
    assert ball.speed_multiplier == pytest.approx(prev_speed * 1.2)
