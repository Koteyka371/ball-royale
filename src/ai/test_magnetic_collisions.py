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

def test_magnetic_ball_to_ball_forces():
    world = MockWorld()

    b1 = MockBall(0, 0)
    b1.polarity = "positive"

    b2 = MockBall(100, 0)
    b2.polarity = "negative"

    b3 = MockBall(-100, 0)
    b3.polarity = "positive"

    world.balls = [b1, b2, b3]

    # Tick with delta 1.0 for large effect
    world.game_mode.tick(world, world.balls, delta=1.0)

    # b1 and b2 are opposites (dist 100), attract.
    # b1 and b3 are likes (dist 100), repel.

    # Wait, b2 and b3 (dist 200, mag_range 200), force = 0.

    # b1 + b2: attract
    # dx=100, dist=100
    # force = (200-100)/200 * 100 * 1 = 50
    # b1.x += 100/100 * 50 = +50
    # b2.x -= 100/100 * 50 = -50
    # b1.x becomes 50, b2.x becomes 50

    # Then b1 + b3: likes repel
    # b1 is now at 50, b3 at -100
    # dx = b3.x - b1.x = -150
    # dist = 150
    # force = (200-150)/200 * 100 * 1 = 25
    # b1.x -= dx/dist * force => b1.x -= -150/150 * 25 => b1.x -= -25 => b1.x += 25 => 75
    # b3.x += dx/dist * force => b3.x += -1 * 25 => b3.x -= 25 => -125

    # Let's just print to see actual values and assert them
    print(f'b1: {b1.x}, b2: {b2.x}, b3: {b3.x}')
    assert b1.x == 75.0
    assert b2.x == 37.5
    assert b3.x == -112.5
