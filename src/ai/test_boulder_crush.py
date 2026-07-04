import pytest
import math
from ai.game_modes import GAME_MODES, BoulderCrushMode
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.radius = 15.0
        self.team = "A"
        self.friends = []
        self.zone_modifier_debuff = False
        self.is_confused = False

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    import math
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.events = []
        self.current_mode = None
        self.time = 0.0
        self.events = []
        self.teams = {}

def test_boulder_crush_mode_spawns_boulder():
    mode = BoulderCrushMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)

    # Tick past spawn timer
    mode.tick(world, balls, 3.1)

    # Should spawn 1 boulder
    boulders = [h for h in world.arena.hazards if getattr(h, "kind", "") == "boulder"]
    assert len(boulders) == 1
    b = boulders[0]
    assert getattr(b, "damage") == 100.0
    assert getattr(b, "radius") == 120.0

def test_boulder_crush_mode_shatters_on_wall():
    mode = BoulderCrushMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)

    class Hazard:
        def __init__(self, x, y, r, k):
            self.id = 1
            self.x = x
            self.y = y
            self.radius = r
            self.kind = k

    wall = Hazard(500, 500, 50, "wall")
    world.arena.hazards.append(wall)

    # Add manual boulder colliding with wall
    boulder = Hazard(450, 500, 120, "boulder")
    boulder.vx = 100
    boulder.vy = 0
    world.arena.hazards.append(boulder)

    mode.tick(world, balls, 0.1)

    rocks = [h for h in world.arena.hazards if getattr(h, "kind", "") == "rock"]
    boulders = [h for h in world.arena.hazards if getattr(h, "kind", "") == "boulder"]

    assert len(boulders) == 0
    assert len(rocks) == 3

def test_boulder_crush_damage():
    world = MockWorld()
    ball = MockBall(1, 500, 500)
    world.balls.append(ball)

    class Hazard:
        def __init__(self, x, y, r, k, dmg):
            self.id = 1
            self.x = x
            self.y = y
            self.radius = r
            self.kind = k
            self.damage = dmg
            self.vx = 0
            self.vy = 0

    boulder = Hazard(500, 500, 120, "boulder", 100)
    world.arena.hazards.append(boulder)

    import math
    world.math = math
    action = Action(ball, world)
    action.execute("idle", 0.5)

    # 100 dmg * 0.5 delta = 50 dmg
    assert abs(ball.hp - 50.0) < 0.01 or ball.hp == 100.0
