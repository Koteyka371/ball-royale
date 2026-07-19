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

def test_repulsion_zone_push_scaling():
    w = MockWorld()

    h = MockHazard(1, 0, 0, 150.0, "repulsion_zone")
    h.damage = 0.0
    h.owner_id = 99
    w.arena.hazards.append(h)

    # Ball near the center
    t_near = MockBall(2, 10, 0)
    t_near.team = "B"
    t_near.vx = 0.0
    t_near.vy = 0.0
    w.balls.append(t_near)

    # Ball near the edge
    t_far = MockBall(3, 140, 0)
    t_far.team = "B"
    t_far.vx = 0.0
    t_far.vy = 0.0
    w.balls.append(t_far)

    a_near = Action(t_near, w)
    def _mock_get_enemies_near(): return []
    a_near._get_enemies = _mock_get_enemies_near
    initial_x_near = t_near.x
    a_near.execute("idle", 0.1)

    a_far = Action(t_far, w)
    def _mock_get_enemies_far(): return []
    a_far._get_enemies = _mock_get_enemies_far
    initial_x_far = t_far.x
    a_far.execute("idle", 0.1)

    push_dist_near = t_near.x - initial_x_near
    push_dist_far = t_far.x - initial_x_far

    assert push_dist_near > push_dist_far, f"Expected push near center ({push_dist_near}) to be greater than push near edge ({push_dist_far})"
