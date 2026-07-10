import pytest
from ai.action import Action

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockWorld:
    def __init__(self, arena, balls, boosters=None):
        self.arena = arena
        self.balls = balls
        self.boosters = boosters if boosters else []
        self.entities = balls
        self.next_id = 1000

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

def test_black_hole_grenade_collect_and_deploy():
    brawler = MockBall(1, 0, 0, team="teamA")
    enemy = MockBall(2, 50, 0, team="teamB")

    booster = MockEntity(3, 0, 0, kind="black_hole_grenade_booster")

    arena = MockArena([booster])
    world = MockWorld(arena, [brawler, enemy], boosters=[booster])

    action = Action(brawler, world)

    # 1. Collect booster
    action.execute("collect_booster", 1.0)

    assert "black_hole_grenade" in brawler.inventory
    assert booster not in arena.hazards
    assert booster not in world.boosters

    # 2. Throw grenade
    action.execute("attack", 1.0)

    assert "black_hole_grenade" not in brawler.inventory

    assert len(arena.hazards) == 1
    grenade = arena.hazards[0]
    assert grenade.kind == "thrown_black_hole_grenade"
    assert getattr(grenade, "duration", 0.0) == 0.5
    assert getattr(grenade, "owner_id", None) == brawler.id

    # 3. Explode into black hole
    action2 = Action(brawler, world)
    action2.execute("attack", 2.0)

    assert len(arena.hazards) == 1
    bh = arena.hazards[0]
    assert bh.kind == "black_hole"
    assert getattr(bh, "duration", 0.0) == 5.0
    assert getattr(bh, "owner_id", None) == brawler.id
