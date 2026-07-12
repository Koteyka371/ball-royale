import pytest
from ai.game_modes import GAME_MODES
from ai.action import Action
import math

class MockBall:
    def __init__(self, x=500.0, y=500.0, hp=100.0, stamina=100.0, alive=True):
        self.x = x
        self.y = y
        self.hp = hp
        self.stamina = stamina
        self.alive = alive
        self.ball_type = "test"
        self.team = "test"
        self.id = id(self)
        self.supercharge_timer = 0.0

class MockArena:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.hazards = []
        self.items = []
        self.boosters = []
        self.weather = "sunny"

    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena(1000, 1000)
        self.events = []

    def get_nearby_entities(self, ball, radius):
        return {'boosters': [], 'hazards': [], 'enemies': [], 'allies': [], 'items': []}

def test_scorching_sun_mode():
    mode = GAME_MODES.get("scorching_sun")
    assert mode is not None

    world = MockWorld()
    # b1 is exactly at center, safely inside
    b1 = MockBall(500, 500)
    # b2 is at corner, safely outside initially? 1000/1.2 = 833. center is 500,500.
    # corner 0,0 distance is ~707. 707 < 833.
    # We need a position outside 833 radius.
    # But arena is 1000x1000. Maximum distance from center is corner (0,0), which is 707.
    # So if arena is 1000x1000, 833 radius covers the WHOLE map!
    # Wait, arena_width / 1.2 is 1000 / 1.2 = 833.
    # And we decrease by 10 per second.
    # If delta is large enough, radius will shrink.

    b2 = MockBall(0, 0)

    balls = [b1, b2]
    mode.setup(world, balls)

    # Fast forward time to shrink zone significantly (shrink by 10 per sec, so 20 seconds = 200 shrink)
    # 833 - 200 = 633.
    # Let's just tick for 1 sec at a time until radius < 700.
    for _ in range(20):
        mode.tick(world, balls, 1.0)

    assert mode.zone_radius < 700

    # Reset stats
    b1.hp = 100.0
    b1.stamina = 100.0
    b2.hp = 100.0
    b2.alive = True
    b1.alive = True
    b2.alive = True
    b1.alive = True
    b2.stamina = 100.0

    # Tick again
    mode.tick(world, balls, 1.0)

    # b1 still at center
    assert b1.hp == 100.0
    assert b1.stamina == 100.0

    # b2 is outside, should take damage and stamina drain
    assert b2.hp < 100.0
    assert b2.stamina < 100.0
    assert math.isclose(b2.hp, 100.0 - 15.0)
    assert math.isclose(b2.stamina, 100.0 - 20.0)
