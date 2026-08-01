from src.ai.action import Action
import math

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.speed = 100
        self.base_speed = 100
        self.is_emped = False
        self.emp_immunity_timer = 0
        self.emp_timer = 0
        self.skill_timer = 0
        self.team = "blue"
        self.alive = True
        self.charge_level = 0
        self.damage = 10
        self.hp = 100
        self.max_hp = 100
        self.inventory = ["thermal_boots", "advanced_optics", "thermal_goggles"]
        self.thermal_boots_timer = 10.0
        self.vision_booster_timer = 10.0
        self.vision_booster_applied = True
        self.stealth_drone_timer = 10.0
        self.has_stealth_drone = True
        self.base_perception_radius = 200.0
        self.perception_radius = 300.0
        self.radius = 10.0
        self.is_frictionless = False
        self.invisible = False

class MockHazard:
    def __init__(self, id, x, y, kind):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 50.0
        self.owner_id = 999
        self.trap_variant = "emp"
        self.active = True
        self.duration = 10.0
        self.trap_level = 1
        self.owner_team = "red"
        self.hologram_spawned = False
        self.last_updated_tick = -1

class MockArena:
    def __init__(self):
        self.hazards = []
        self.weather = "clear"
        self.width = 1000
        self.height = 1000
        self.shrinking = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
        self.events = []
        self.boosters = []

    def _deal_damage(self, attacker, target, damage=None):
        pass

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "hazards": self.arena.hazards, "boosters": [], "items": [], "projectiles": []}

def test_emp_trap_trigger():
    b = MockBall(1, 0, 0)
    w = MockWorld()
    w.balls.append(b)
    h = MockHazard(1, 0, 0, "trap")
    w.arena.hazards.append(h)

    action = Action(b, w)

    # Run a tick where ball intersects the hazard
    b.x = 0
    b.y = 0

    # We must mock get_nearby_entities better to have hazard returned
    w.get_nearby_entities = lambda ball, r: {"enemies": [], "allies": [], "hazards": [h], "boosters": [], "items": [], "projectiles": []}

    action.execute("idle", 0.016)

    assert b.is_emped == True
    assert b.thermal_boots_timer == 0.0
    assert b.vision_booster_timer == 0.0
    assert getattr(b, "vision_booster_applied", True) == False
    assert b.perception_radius == b.base_perception_radius
    assert b.stealth_drone_timer == 0.0
    assert b.has_stealth_drone == False
    assert "thermal_boots" not in b.inventory
    assert "thermal_goggles" not in b.inventory
    assert "advanced_optics" not in b.inventory
