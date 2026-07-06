import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

    def update_zone(self, *args):
        pass

    def clamp_position(self, *args):
        return (0, 0, False)

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.events = []
        self.width = 1000
        self.height = 1000

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": self.boosters}

    def add_event(self, event_type, data):
        pass

    def _deal_damage(self, attacker, target):
        pass

class MockBall:
    def __init__(self, id, x, y, team, skill, inventory):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.team = team
        self.skill = skill
        self.active_skill = skill
        self.SKILL = skill
        self.inventory = inventory
        self.alive = True
        self.is_decoy = False
        self.speed = 10.0
        self.radius = 10.0
        self.hp = 100
        self.base_speed = 10.0
        self.perception_radius = 500.0
        self.skill_timer = 0.0
        self.skill_cooldown = 0.0
        self.used_skill_count = 0
        self.ball_type = "base"
        self.is_flying = False
        self.current_action = "none"

class MockBooster:

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0
        self.damage = 0.0

def test_skill_swap_trap():
    world = MockWorld()
    b1 = MockBall(1, 10, 10, "A", "dash", ["sword"])
    b2 = MockBall(2, 50, 50, "B", "heal", ["shield"])
    world.balls.extend([b1, b2])

    trap = MockBooster(10, 10, "skill_swap_trap")
    world.boosters.append(trap)
    world.arena.hazards.append(trap)

    action = Action(b1, world)

    # 1. Collect
    action.execute("collect_booster", 1.0)

    # Verify trap consumed
    assert trap not in world.boosters
    assert trap not in world.arena.hazards

    # Verify skills swapped
    assert b1.skill == "heal"
    assert b1.active_skill == "heal"
    assert b1.inventory == ["shield"]
    assert b1.skill_swap_timer > 0.0

    assert b2.skill == "dash"
    assert b2.active_skill == "dash"
    assert b2.inventory == ["sword"]
    assert b2.skill_swap_timer > 0.0

    # 2. Timer decrement (advance time by 15s)
    action.execute("none", 15.0)

    # Check that skills restored
    assert b1.skill == "dash"
    assert b1.active_skill == "dash"
    assert b1.inventory == ["sword"]

    # Check b2 restoration via action
    action2 = Action(b2, world)
    action2.execute("none", 15.0)

    assert b2.skill == "heal"
    assert b2.active_skill == "heal"
    assert b2.inventory == ["shield"]
