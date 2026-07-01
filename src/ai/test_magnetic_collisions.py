import pytest
from ai.action import Action
from ai.game_modes import MagneticCollisionsMode

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10.0
        self.traits = []
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.is_dashing = False
        self.alive = True

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.game_mode = MagneticCollisionsMode()

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [b for b in self.balls if b != ball], "allies": []}

def test_magnetic_collisions():
    world = MockWorld()
    # Initially overlap: radius 10 each, so min dist is 20.
    # Dist is 10, so overlap is 10.
    b1 = MockBall(0, 0)
    b2 = MockBall(10, 0)
    world.balls = [b1, b2]

    action1 = Action(b1, world)

    # We resolve collisions.
    # dx = b1.x - b2.x = 0 - 10 = -10
    # dy = 0
    # dist = 10. overlap = 20 - 10 = 10
    # nx = -1.0, ny = 0.0
    # knockback_mult = -0.5
    # b1.x += (-1.0) * 10 * (-0.5) = +5.0

    action1._resolve_collisions()

    assert b1.x == 5.0
    assert b1.y == 0.0
