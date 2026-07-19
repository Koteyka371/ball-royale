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

def test_event_horizon_trap():
    w = MockWorld()

    h = MockHazard(1, 0, 0, 300.0, "event_horizon_trap")
    h.damage = 0.0
    h.owner_id = 99
    w.arena.hazards.append(h)

    t = MockBall(2, 50, 0)
    t.team = "B"
    w.balls.append(t)

    a = Action(t, w)

    # Mock _get_enemies
    def _mock_get_enemies():
        return [t]
    a._get_enemies = _mock_get_enemies

    a.execute("idle", 0.1)

    assert t.x < 50
    assert getattr(t, "speed_multiplier", 1.0) == 0.3
    assert getattr(t, "defense_multiplier", 1.0) == 2.0

    t.x = 10
    t.y = 0

    a.execute("idle", 0.1)
    assert getattr(h, "duration", 10.0) == 0.0

    a.execute("idle", 0.1)
    assert getattr(t, "hp", 100) == 50
