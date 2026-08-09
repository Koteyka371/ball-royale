import pytest
from ai.action import Action
import math

class MockHazard:
    def __init__(self, id, x, y, radius, kind, damage):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.active = True

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []

    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

    def get_nearby_entities(self, ball, radius):
        return [b for b in self.balls if b != ball]

class MockBall:
    def __init__(self, id, x, y, vx, vy, team):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.team = team
        self.radius = 10.0
        self.mass = 1.0
        self.alive = True
        self.is_flying = False
        self.intangible = False
        self.intangible_timer = 0.0
        self.phase_booster_timer = 0.0
        self.ghost_booster_timer = 0.0
        self.speed = 500.0

def test_high_speed_collision_spawns_black_hole():
    world = MockWorld()

    # Setup two balls moving fast towards each other
    # Speed > 400
    b1 = MockBall(1, 500.0, 500.0, 500.0, 0.0, "team1")
    b2 = MockBall(2, 510.0, 500.0, -500.0, 0.0, "team2")

    world.balls = [b1, b2]

    # We will simulate the execution of `_resolve_collisions`
    action = Action(b1, world)

    action._resolve_collisions()

    # Check if a black hole hazard was spawned
    black_holes = [h for h in world.arena.hazards if h.kind == "black_hole"]
    assert len(black_holes) == 1

    bh = black_holes[0]
    assert bh.x == 500.0 # Midpoint
    assert bh.y == 500.0
    assert getattr(bh, "duration", 0) == 2.0
    assert getattr(bh, "pull_strength", 0) == 300.0

    # Verify event was emitted
    bh_events = [e for e in world.events if e["type"] == "visual_effect" and e["data"]["type"] == "black_hole_spawn"]
    assert len(bh_events) == 1
    assert bh_events[0]["data"]["x"] == 500.0

def test_low_speed_collision_no_black_hole():
    world = MockWorld()

    # Setup two balls moving slowly towards each other
    # Speed < 400
    b1 = MockBall(1, 500.0, 500.0, 100.0, 0.0, "team1")
    b2 = MockBall(2, 510.0, 500.0, -100.0, 0.0, "team2")

    world.balls = [b1, b2]

    action = Action(b1, world)
    action._resolve_collisions()

    # Check that no black hole hazard was spawned
    black_holes = [h for h in world.arena.hazards if getattr(h, "kind", "") == "black_hole"]
    assert len(black_holes) == 0
