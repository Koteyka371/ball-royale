import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockWorld:
    def __init__(self, arena, balls, boosters=None, projectiles=None):
        self.arena = arena
        self.balls = balls
        self.boosters = boosters if boosters else []
        self.projectiles = projectiles if projectiles else []
        self.entities = balls
        self.next_id = 1000
        self.events = []

    def get_nearby_entities(self, entity, radius):
        return {
            "enemies": [b for b in self.balls if b != entity],
            "allies": [],
            "boosters": self.boosters
        }

class MockEntity:
    def __init__(self, id, x, y, kind=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.ball_type = "booster"
        self.active = True

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockBall:
    def __init__(self, id, x, y, team="teamA"):
        self.id = id
        self.x = x
        self.y = y
        self.skill = "none"
        self.skill_timer = 0.0
        self.radius = 10.0
        self.alive = True
        self.ball_type = "brawler"
        self.team = team
        self.hp = 100
        self.speed = 10
        self.base_speed = 10
        self.stamina = 100
        self.inventory = []

class MockProjectile:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0

class MockHazard:
    def __init__(self, id, x, y, kind):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 10.0
        self.duration = 10.0
        self.damage = 10.0

def test_miniature_black_hole():
    brawler = MockBall(1, 0, 0, team="teamA")
    enemy = MockBall(2, 50, 0, team="teamB")

    booster = MockEntity(3, 0, 0, kind="miniature_black_hole_item")

    arena = MockArena([booster])
    world = MockWorld(arena, [brawler, enemy], boosters=[booster])

    # 1. Collect booster
    action = Action(brawler, world)
    action.execute("collect_booster", 1.0)

    assert "miniature_black_hole" in brawler.inventory
    assert booster not in arena.hazards

    # 2. Deploy it
    action.execute("attack", 1.0)
    assert "miniature_black_hole" not in brawler.inventory

    assert len(arena.hazards) == 1
    bh = arena.hazards[0]
    assert bh.kind == "mini_black_hole_hazard"
    assert hasattr(bh, "vx")

    # Add a hazard and projectile to suck in
    h1 = MockHazard(10, bh.x + 10, bh.y + 10, "fire")
    p1 = MockProjectile(20, bh.x - 10, bh.y - 10)

    arena.hazards.append(h1)
    world.projectiles.append(p1)

    # Run a tick to pull in
    # Use Action from enemy to process hazards so brawler doesn't interfere
    action2 = Action(enemy, world)
    bh.duration = 0.5 # About to expire
    action2.execute("idle", 0.1)

    # They should be collected
    assert h1 not in arena.hazards
    assert p1 not in world.projectiles
    assert h1 in bh.collected_hazards
    assert p1 in bh.collected_projectiles

    # Expire and explode
    bh.duration = 0.1
    action2.execute("idle", 0.1)

    # Exploded
    assert bh not in arena.hazards
    assert h1 in arena.hazards
    assert p1 in world.projectiles

    # h1 and p1 should have velocity set
    assert hasattr(h1, "vx") and hasattr(h1, "vy")
    assert h1.vx != 0 or h1.vy != 0
    assert p1.vx != 0 or p1.vy != 0
