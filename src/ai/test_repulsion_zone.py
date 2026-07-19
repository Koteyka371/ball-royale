from ai.action import Action
class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.entities = []
        self.next_id = 1000
        self.flare_light_timer = 0.0

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [], "allies": [], "hazards": [], "boosters": []}
    def add_event(self, kind, payload):
        pass

class MockHazard:
    def __init__(self, id, x, y, radius, kind, damage=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.duration = 5.0
        self.owner_id = 1
        self.active = True

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.team = "A"
        self.ball_type = "brawler"
        self.hp = 100
        self.max_hp = 100
        self.inventory = []
        self.intangible = False
        self.speed = 50
        self.stamina = 100
        self.max_stamina = 100
        self.original_base_damage = 10
        self.base_damage = 10
        self.base_speed = 50
        self.traits = []

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False

def test_repulsion_zone():
    w = MockWorld()

    h = MockHazard(1, 0, 0, 150.0, "repulsion_zone")
    h.damage = 0.0
    h.owner_id = 99
    w.arena.hazards.append(h)

    t = MockBall(2, 50, 0)
    t.team = "B"
    t.vx = 0.0
    t.vy = 0.0
    w.balls.append(t)

    a = Action(t, w)

    # Mock _get_enemies
    def _mock_get_enemies():
        return []
    a._get_enemies = _mock_get_enemies

    # Move closer in idle, should be pushed away
    initial_x = t.x
    a.execute("idle", 0.1)

    # In action.py idle usually keeps you still or moves slightly. But the hazard check happens every frame.
    # The hazard will push the ball outward from (0,0). So ball at (50,0) will be pushed to the right.
    assert t.x > initial_x, f"Expected {t.x} to be > {initial_x} due to repulsion"
