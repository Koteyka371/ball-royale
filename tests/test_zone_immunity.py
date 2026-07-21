import math
from src.ai.action import Action

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100.0
        self.alive = True
        self.ball_type = "normal"
        self.radius = 10.0
        self.team = "Red"
        self.zone_immunity_timer = 0.0

class MockArena:
    def __init__(self):
        self.safe_zone_center = (0, 0)
        self.safe_zone_radius = 50.0
        self.hazards = []

    def update_zone(self, tick, delta):
        pass

class MockEntity:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 5.0
        self.duration = 5.0
        self.damage = 0.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick = 0
        self.current_mode_name = "test"
        self.entities = []

    def _get_entities_in_radius(self, x, y, r):
        return []

    def get_nearby_entities(self, ball, radius):
        boosters = [e for e in self.entities if getattr(e, "kind", None) in ["zone_immunity"]]
        return {
            "enemies": [],
            "allies": [],
            "boosters": boosters
        }

def test_zone_immunity_damage_blocked():
    ball = MockBall(100, 100) # Outside radius 50
    world = MockWorld()
    world.entities = [ball]
    action = Action(ball, world)

    # 1. No immunity
    action.execute("idle", 1.0)
    ball.hp = 100.0
    ball.alive = True

    # 2. Immunity
    ball.zone_immunity_timer = 5.0
    ball.hp = -100.0
    ball.hp = 100.0
    ball.alive = True
    hp_before = ball.hp
    action.execute("idle", 1.0)
    assert ball.hp == hp_before # no damage taken
    assert ball.zone_immunity_timer == 4.0 # timer reduced

def test_collect_zone_immunity_powerup():
    ball = MockBall(0, 0)
    powerup = MockEntity(0, 5, "zone_immunity")
    world = MockWorld()
    world.arena.hazards.append(powerup)
    world.entities = [ball, powerup]

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    # Check immunity granted
    assert ball.zone_immunity_timer == 5.0
    # Check powerup removed
    assert powerup not in world.arena.hazards
