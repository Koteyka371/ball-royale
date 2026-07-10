import pytest
from ai.action import Action
from arena.procedural_arena import Hazard

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
        self.hp = 50
        self.max_hp = 100
        self.speed = 10
        self.base_speed = 10
        self.stamina = 100
        self._base_speed_set = True

        # statuses
        self.stun_timer = 0.0
        self.burn_timer = 0.0
        self.poison_timer = 0.0
        self.wet_timer = 0.0

def test_weather_shield_collect_and_use():
    brawler = MockBall(1, 0, 0, team="teamA")
    # Apply some status effects to brawler
    brawler.stun_timer = 2.0
    brawler.wet_timer = 3.0

    booster = MockEntity(3, 0, 0, kind="weather_shield_item")

    arena = MockArena([booster])
    world = MockWorld(arena, [brawler], boosters=[booster])

    action = Action(brawler, world)

    # 1. Collect booster
    action.execute("collect_booster", 1.0)

    assert "weather_shield_item" in brawler.inventory
    assert booster not in arena.hazards
    assert booster not in world.boosters

    # 2. Use item (should cleanse effects since brawler has wet_timer and stun_timer)
    action.execute("flee", 1.0)

    assert "weather_shield_item" not in brawler.inventory

    # Effects should be absorbed (cleansed)
    assert brawler.stun_timer == 0.0
    assert brawler.wet_timer == 0.0

    # Regeneration buff should be active
    assert getattr(brawler, "weather_shield_regen_timer", 0.0) > 0.0
    assert brawler.hp > 50.0
