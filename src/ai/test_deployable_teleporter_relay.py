import pytest
from ai.action import Action

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self, arena, balls, boosters=None):
        self.arena = arena
        self.balls = balls
        self.boosters = boosters if boosters else []
        self.entities = balls
        self.next_id = 1000
        self.tick = 1

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

def test_deployable_teleporter_relay_collect_and_deploy():
    brawler = MockBall(1, 0, 0, team="teamA")

    booster = MockEntity(3, 0, 0, kind="deployable_teleporter_relay")

    arena = MockArena([booster])
    world = MockWorld(arena, [brawler], boosters=[booster])

    action = Action(brawler, world)

    # 1. Collect booster
    action.execute("collect_booster", 1.0)

    assert "deployable_teleporter_relay" in brawler.inventory
    assert booster not in arena.hazards
    assert booster not in world.boosters

    # 2. Deploy relays
    action.execute("attack", 1.0)

    assert "deployable_teleporter_relay" not in brawler.inventory

    # It should have deployed two teleporters
    assert len(arena.hazards) == 2
    t1 = arena.hazards[0]
    t2 = arena.hazards[1]

    assert t1.kind == "teleporter"
    assert t2.kind == "teleporter"

    # Check that they target each other
    assert getattr(t1, "target_x") == t2.x
    assert getattr(t1, "target_y") == t2.y
    assert getattr(t2, "target_x") == t1.x
    assert getattr(t2, "target_y") == t1.y

    # Check duration
    assert getattr(t1, "duration") == 15.0
    assert getattr(t2, "duration") == 15.0
