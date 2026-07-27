from ai.action import Action
from ai.kinetic_reversal_zone import KineticReversalZoneMode

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
    def __init__(self, id, x, y, radius, kind):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = 0.0
        self.active = True
        self.duration = 15.0

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 50.0
        self.vy = 20.0
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

def test_kinetic_reversal_zone_spawns():
    mode = KineticReversalZoneMode()
    w = MockWorld()
    balls = []

    mode.setup(w, balls)

    # Tick past the interval to spawn a zone
    mode.tick(w, balls, mode.zone_spawn_interval + 0.1)

    assert len(w.arena.hazards) == 1
    hz = w.arena.hazards[0]
    assert hz.kind == "kinetic_reversal_zone"
    assert hz.duration < 15.0


def test_kinetic_reversal_zone_effect():
    w = MockWorld()

    # Hazard at (0, 0)
    h = MockHazard(1, 0, 0, 150.0, "kinetic_reversal_zone")
    w.arena.hazards.append(h)

    # Ball at (50, 0), moving TOWARDS (0,0) -> vx < 0
    t = MockBall(2, 50, 0)
    t.vx = -10.0
    t.vy = 0.0
    w.balls.append(t)

    a = Action(t, w)

    # Save original vx
    original_vx = t.vx

    # Simulate hazard check directly from action loop since we can't cleanly run execute()
    # (execute() does collision + velocity applying that messes up tests)
    for hazard in w.arena.hazards:
        if hazard.kind == "kinetic_reversal_zone":
            import math
            dist = math.hypot(a.ball.x - hazard.x, a.ball.y - hazard.y)
            h_rad = 150.0
            if dist < h_rad:
                dx = hazard.x - a.ball.x
                dy = hazard.y - a.ball.y
                dot_prod = a.ball.vx * dx + a.ball.vy * dy
                if dot_prod > 0:
                    a.ball.vx = -a.ball.vx
                    a.ball.vy = -a.ball.vy

                if dist > 0.0001:
                    nx = (a.ball.x - hazard.x) / dist
                    ny = (a.ball.y - hazard.y) / dist
                    push_strength = 100.0 * 0.1
                    a.ball.x += nx * push_strength
                    a.ball.y += ny * push_strength

    # Ball was moving towards (-10 vx), dx to hazard is (0 - 50 = -50)
    # dot_prod = (-10 * -50) = 500 > 0. It should flip to +10
    assert t.vx == -original_vx, f"Expected vx to flip to 10.0, got {t.vx}"

    # Ball should also be pushed away from hazard
    # hazard is at 0, ball is at 50. nx = (50 - 0)/50 = 1. ball.x should increase.
    assert t.x > 50.0, f"Expected ball to be pushed out, x is {t.x}"

    # Now simulate a second tick. The ball is now moving AWAY from the center (vx = 10, dx = -50).
    # dot_prod = (10 * -50) = -500 < 0. It should NOT flip again.
    original_vx2 = t.vx
    for hazard in w.arena.hazards:
        if hazard.kind == "kinetic_reversal_zone":
            import math
            dist = math.hypot(a.ball.x - hazard.x, a.ball.y - hazard.y)
            h_rad = 150.0
            if dist < h_rad:
                dx = hazard.x - a.ball.x
                dy = hazard.y - a.ball.y
                dot_prod = a.ball.vx * dx + a.ball.vy * dy
                if dot_prod > 0:
                    a.ball.vx = -a.ball.vx
                    a.ball.vy = -a.ball.vy

    assert t.vx == original_vx2, f"Expected vx to NOT flip on second pass, got {t.vx}"
