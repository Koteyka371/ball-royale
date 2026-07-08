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
        self.hp = 100
        self.speed = 10
        self.base_speed = 10
        self.stamina = 100
        self._base_speed_set = True

        # statuses
        self.stun_timer = 0.0
        self.burn_timer = 0.0
        self.poison_timer = 0.0

def test_status_absorber_collect_and_throw():
    brawler = MockBall(1, 0, 0, team="teamA")
    # Apply some status effects to brawler
    brawler.stun_timer = 2.0
    brawler.burn_timer = 3.0

    enemy = MockBall(2, 100, 0, team="teamB")

    booster = MockEntity(3, 0, 0, kind="status_absorber_item")

    arena = MockArena([booster])
    world = MockWorld(arena, [brawler, enemy], boosters=[booster])

    action = Action(brawler, world)

    # 1. Collect booster
    action.execute("collect_booster", 1.0)

    assert "status_absorber_item" in brawler.inventory
    assert booster not in arena.hazards
    assert booster not in world.boosters

    # 2. Throw at enemy
    # Since they have status effects and the item, they should cleanse themselves and throw a hazard
    action.execute("attack", 1.0)

    assert "status_absorber_item" not in brawler.inventory

    # Effects should be absorbed (cleansed)
    assert brawler.stun_timer == 0.0
    assert brawler.burn_timer == 0.0

    # Hazard should be in the arena
    assert len(arena.hazards) == 1
    thrown_h = arena.hazards[0]
    assert thrown_h.kind == "thrown_status_absorber"
    assert thrown_h.owner_id == brawler.id
    assert thrown_h.absorbed_effects["stun_timer"] == 2.0
    assert thrown_h.absorbed_effects["burn_timer"] == 3.0

    # 3. Simulate hit on enemy (move hazard to enemy)
    thrown_h.x = enemy.x
    thrown_h.y = enemy.y

    enemy_action = Action(enemy, world)
    enemy_action.execute("idle", 1.0)

    # Enemy should take damage and receive statuses
    assert enemy.hp == 90 # 10 damage
    assert enemy.stun_timer == 2.0
    assert enemy.burn_timer == 3.0

    # Hazard should be removed
    assert len(arena.hazards) == 0
