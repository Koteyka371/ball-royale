import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self, x, y, team=1, cosmetic="tethered_boots", id=1):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.cosmetic = cosmetic
        self.team = team
        self.alive = True
        self.ball_type = "normal"
        self.in_mirror_dimension = False
        self.hp = 100
        self.radius = 10.0
        self.mass = 1.0

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __contains__(self, key):
        return hasattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def get_meta(self, key, default=None):
        return getattr(self, key, default)

    def has_meta(self, key):
        return hasattr(self, key)

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []

    def get_nearby_entities(self, ball, radius):
        allies = [b for b in self.balls if b.team == ball.team and b.id != ball.id and b.alive]
        enemies = [b for b in self.balls if b.team != ball.team and b.id != ball.id and b.alive]
        # _resolve_collisions iterates over get_nearby_entities()['allies'] and ['enemies'] or just list depending on implementation
        # let's return a list as some places expect a list
        return allies + enemies

    def add_event(self, event_type, data=None):
        pass

def test_tethered_boots_knockback_and_status_share():
    world = MockWorld()

    # b1 has tethered_boots
    b1 = MockBall(100, 100, team=1, cosmetic="tethered_boots", id=1)
    b1.speed_boost_timer = 5.0

    # b2 is an ally, nearby
    b2 = MockBall(120, 100, team=1, cosmetic="none", id=2)
    b2.speed_boost_timer = 1.0 # Should be updated to 5.0

    # b3 is an enemy that collides with b1
    b3 = MockBall(90, 100, team=2, cosmetic="none", id=3)
    b3.vx = 100.0 # moving right

    world.balls.extend([b1, b2, b3])
    action = Action(b1, world)
    action.world.get_nearby_entities = lambda b, r: {"allies": [b2], "enemies": [b3]}

    # For _resolve_collisions we might need a specific return type. Let's patch world for it.
    world.get_nearby_entities = lambda b, r: [b2, b3] if isinstance(r, float) or isinstance(r, int) else [b2, b3]

    # Check what get_nearby_entities returns for `_get_allies` vs `_resolve_collisions`
    # We will override _get_allies temporarily to avoid any issues just in case
    action._get_allies = lambda: [b2]

    # Trigger collision resolution manually
    # b3 is at x=90, b1 is at x=100. dx=10, dy=0.
    # min_dist = 20. dist = 10. overlap = 10. nx = 1.0, ny = 0.0
    action._resolve_collisions()

    assert math.isclose(b1.x, 105.0), f"Expected b1.x=105.0, got {b1.x}"
    assert math.isclose(b2.x, 125.0), f"Expected b2.x=125.0, got {b2.x}"

    # Status sharing check
    assert b2.speed_boost_timer == 5.0, "Ally should inherit the highest speed_boost_timer"

def test_tethered_boots_no_ally():
    world = MockWorld()

    b1 = MockBall(100, 100, team=1, cosmetic="tethered_boots", id=1)
    b3 = MockBall(90, 100, team=2, cosmetic="none", id=3)

    world.balls.extend([b1, b3])
    action = Action(b1, world)

    action._get_allies = lambda: []
    world.get_nearby_entities = lambda b, r: [b3]

    action._resolve_collisions()

    # Since no ally, b1 only takes its half (50%) and the rest is lost (absorbed)
    assert math.isclose(b1.x, 105.0), f"Expected b1.x=105.0, got {b1.x}"
