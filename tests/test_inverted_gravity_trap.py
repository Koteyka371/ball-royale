import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team, ball_type="default"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.speed = 10.0
        self.inventory = []
        self.action = None

class MockHazard:
    def __init__(self, id, x, y, radius, kind, damage=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.duration = 10.0
        self.is_inverted = False
        self.owner_id = None

class MockBooster:
    def __init__(self, id, x, y, kind):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15.0
        self.kind = kind
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.weather = "clear"

    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.tick = 0
        self.game_mode = None

    def get_nearby_entities(self, ball, radius):
        return {"boosters": self.boosters, "hazards": self.arena.hazards, "enemies": []}

    def _deal_damage(self, attacker, target, dmg):
        target.hp -= dmg

def test_inverted_gravity_trap_booster_pickup():
    ball = MockBall("p1", 500, 500, "team1")
    world = MockWorld()

    booster = MockBooster(1, 500, 500, "inverted_gravity_trap_booster")
    world.boosters.append(booster)

    action = Action(ball, world)
    # The nearest logic in execute() uses world.get_nearby_entities, wait actually execute() has a big `min(items, ...)` block
    # Actually, let's just place the booster right on top of the ball

    # We'll test by setting `ball.ball_type = "broodling"` since that's the main logic path in execute for pickup?
    # Actually, execute() has general pickup logic.
    ball.ball_type = "player"
    # To test pickup, we need to run execute
    # Actually the easiest is to just put the booster in the list and let action run.
    action.execute("idle", 0.1)

    # Wait, the general pickup logic in action.py depends on `target_item`. Let's test if we can deploy it instead.
    # To test deployment:
    ball.inventory.append("inverted_gravity_trap_booster")
    action.execute("defend", 0.1)

    assert "inverted_gravity_trap_booster" not in ball.inventory

    # Check if trap was spawned
    traps = [h for h in world.arena.hazards if h.kind == "inverted_gravity_trap"]
    assert len(traps) == 1
    trap = traps[0]
    assert math.isclose(trap.x, 500, abs_tol=10)
    assert math.isclose(trap.y, 500, abs_tol=10)
    assert trap.owner_id == ball.id

def test_inverted_gravity_trap_trigger():
    ball = MockBall("p1", 500, 500, "team1")
    world = MockWorld()

    # Another ball to trigger it
    trap = MockHazard(1, 500, 500, 40.0, "inverted_gravity_trap", 0.0)
    trap.owner_id = "p2" # Not the ball's owner
    world.arena.hazards.append(trap)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    # Trap should be triggered and set duration to 0
    assert trap.duration == 0.0

    # Should have spawned an inverted gravity well
    gws = [h for h in world.arena.hazards if h.kind == "gravity_well" and getattr(h, "is_inverted", False) == True]
    assert len(gws) == 1
    gw = gws[0]
    assert gw.x == 500
    assert gw.y == 500
    assert gw.owner_id == "p2"

def test_inverted_gravity_well_scatters_items():
    ball = MockBall("p1", 500, 500, "team1")
    world = MockWorld()

    gw = MockHazard(1, 500, 500, 250.0, "gravity_well", 0.0)
    gw.is_inverted = True
    world.arena.hazards.append(gw)

    booster = MockBooster(2, 510, 500, "speed_booster")
    world.boosters.append(booster)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    # The booster should have been pushed outwards along the +x axis
    # x was 510, gw is at 500. dx=10, dist=10, nx=1.
    # push_strength = 200.0 * 0.1 * 5.0 = 100.0
    # Expected new x = 510 + 100 = 610.

    assert booster.x > 510
    assert booster.y == 500
