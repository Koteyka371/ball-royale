import sys
import os
import pytest
import math

sys.path.insert(0, os.path.abspath('src'))
from ai.game_modes import DayNightMode
from ai.action import Action

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.is_night = False

class MockWorld:
    def __init__(self, arena, balls, boosters=None):
        self.arena = arena
        self.balls = balls
        self.boosters = boosters if boosters else []
        self.entities = balls
        self.next_id = 1000
        self.events = []

    def get_nearby_entities(self, entity, radius):
        return {
            "enemies": [b for b in self.balls if b != entity],
            "allies": [],
            "boosters": self.boosters
        }

    def add_event(self, type, data):
        self.events.append((type, data))

class MockEntity:
    def __init__(self, id, x, y, kind=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.ball_type = "booster"
        self.active = True
        self.radius = 10.0

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
        self.hp = 100.0
        self.speed = 10
        self.base_speed = 10
        self.stamina = 100
        self.inventory = []
        self.supercharge_timer = 0.0

def test_deployable_sunlight_mirror():
    # Setup
    brawler = MockBall(1, 100, 100, team="teamA")
    booster = MockEntity(3, 100, 100, kind="sunlight_mirror_booster")
    arena = MockArena([booster])
    world = MockWorld(arena, [brawler], boosters=[booster])
    mode = DayNightMode()
    mode.setup(world, [brawler])

    action = Action(brawler, world)

    # 1. Collect booster
    action.execute("collect_booster", 1.0)
    assert "sunlight_mirror" in brawler.inventory

    # 2. Deploy mirror
    action.execute("attack", 1.0)
    assert "sunlight_mirror" not in brawler.inventory
    assert len(arena.hazards) == 1
    mirror = arena.hazards[0]
    assert mirror.kind == "sunlight_mirror"
    assert mirror.radius == 25.0

    # 3. Simulate sunlight beam hitting the mirror
    mirror.x, mirror.y = 150, 150
    brawler.hp = 100.0
    mode.active_sunlight_beams.append({'x': 150.0, 'y': 150.0, 'radius': 100.0, 'duration': 2.0})

    # Tick DayNightMode
    mode.tick(world, [brawler], delta=0.1)

    # Mirror should have deflected the beam and spawned a new one
    assert len(mode.active_sunlight_beams) == 2
    redirected = mode.active_sunlight_beams[-1]
    assert redirected['radius'] == 75.0
    assert getattr(mirror, "reflect_cooldown", 0.0) == 1.0

    # 4. Tick again to test cooldown decrement
    mode.tick(world, [brawler], delta=0.5)
    assert getattr(mirror, "reflect_cooldown", 0.0) == 0.5

    # Because cooldown > 0, it shouldn't spawn a 3rd beam for the same first beam (or second beam)
    assert len(mode.active_sunlight_beams) == 2
