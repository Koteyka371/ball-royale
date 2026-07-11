import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

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
        self.hp = 80
        self.max_hp = 100
        self.speed = 10
        self.base_speed = 10
        self.stamina = 100
        self._base_speed_set = True

        # statuses
        self.wet = 0.0
        self.cold = 0.0
        self.sandblind = 0.0
        self.poison_timer = 0.0
        self.inventory = []

def test_weather_shield_collect_and_use():
    brawler = MockBall(1, 0, 0, team="teamA")
    # Apply some status effects to brawler
    brawler.wet = 2.0
    brawler.cold = 3.0
    brawler.poison_timer = 1.0

    booster = MockEntity(3, 0, 0, kind="weather_shield_item")

    arena = MockArena([booster])
    world = MockWorld(arena, [brawler], boosters=[booster])

    action = Action(brawler, world)

    # 1. Collect booster
    action.execute("collect_booster", 1.0)

    assert "weather_shield" in brawler.inventory
    assert booster not in arena.hazards
    assert booster not in world.boosters

    # 2. Trigger shield in next action
    action.execute("attack", 1.0)

    assert "weather_shield" not in brawler.inventory

    # Effects should be absorbed (cleansed)
    assert getattr(brawler, "wet", 0.0) == 0.0
    assert getattr(brawler, "cold", 0.0) == 0.0
    assert getattr(brawler, "poison_timer", 0.0) == 0.0

    # Healing should be applied
    assert brawler.hp == 100 # 80 + 20
    assert getattr(brawler, "healing_buff_timer", 0.0) == 5.0
