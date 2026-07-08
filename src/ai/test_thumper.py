import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

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
            "enemies": [b for b in self.balls if b != entity and b.team != entity.team],
            "allies": [b for b in self.balls if b != entity and b.team == entity.team],
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

class MockHazard:
    def __init__(self, id, x, y, radius, kind, damage):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.active = True

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
        self.perception_radius = 250.0

def test_thumper_collect_deploy_and_tick():
    # Setup
    brawler = MockBall(1, 100, 100, team="teamA")
    enemy = MockBall(2, 200, 200, team="teamB")

    # 1. Thumper item collection
    thumper_item = MockEntity(3, 110, 110, kind="thumper_item")
    tornado = MockHazard(4, 500, 500, 50, "tornado", 10.0)
    setattr(tornado, 'vx', 0.0)
    setattr(tornado, 'vy', 0.0)

    arena = MockArena([thumper_item, tornado])
    world = MockWorld(arena, [brawler, enemy], boosters=[thumper_item])
    action = Action(brawler, world)

    action.execute("collect_booster", 1.0)

    # Verify collection
    assert "thumper_item" in brawler.inventory

    # In MockWorld, boosters are passed directly, let's just make sure inventory works

    # 2. Deploy thumper
    # Needs to be "flee", "defend", "attack"
    action.execute("attack", 1.0)

    assert "thumper_item" not in brawler.inventory
    thumpers = [h for h in arena.hazards if getattr(h, "kind", "") == "thumper"]
    assert len(thumpers) == 1
    thumper = thumpers[0]
    assert getattr(thumper, "owner_id") == brawler.id

    # 3. Hazard tick logic
    # Set the pulse timer to trigger the pulse (>= 2.0)
    # The action logic adds delta to the timer. We pass delta=2.0
    action.execute("idle", 2.0)

    # Verify enemy skill timer increased
    assert enemy.skill_timer >= 3.0

    # Verify tornado pulled
    assert getattr(tornado, 'vx', 0) != 0.0
    assert getattr(tornado, 'vy', 0) != 0.0
    assert getattr(tornado, 'vx') < 0 # Moving from 500 to 100
    assert getattr(tornado, 'vy') < 0 # Moving from 500 to 100
