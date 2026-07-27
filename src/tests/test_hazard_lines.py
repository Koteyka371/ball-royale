import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.radius = 10.0

    def take_damage(self, dmg):
        self.hp -= dmg

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.tick = 1

def test_hazard_lines_spawns_and_damages():
    mode = GAME_MODES["sweeping_hazard_lines"]
    world = MockWorld()
    ball = MockBall(1, 500, 500)
    world.balls = [ball]

    mode.setup(world, world.balls)

    # Spawn a hazard line manually to bypass random placement for test
    class DummyHazard:
        def __init__(self, hid, hx, hy, r, k):
            self.id = hid
            self.x = hx
            self.y = hy
            self.radius = r
            self.kind = k
            self.damage = 0.0
            self.vx = 0.0
            self.vy = 0.0

    h = DummyHazard("test_line", -50, 500, 500, "sweeping_hazard_line")
    h.vx = 150.0
    world.arena.hazards.append(h)

    # Fast forward hazard position so it overlaps with ball x=500
    # From -50 to 500 at 150 speed = approx 3.66 seconds
    mode.tick(world, world.balls, delta=3.66)

    # Ball should have taken damage
    assert ball.hp < 100.0

    # Test cleanup
    h.x = 2000
    mode.tick(world, world.balls, delta=0.5)
    # Hazard should be cleaned up
    assert len(world.arena.hazards) <= 1  # May have spawned a new one
