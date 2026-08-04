from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, r): return x, y, False
    def update_zone(self, t, d): pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.balls = []

class MockBall:
    def __init__(self):
        self.x = 50.0
        self.y = 50.0
        self.vx = 50.0
        self.vy = 50.0
        self.radius = 10.0
        self.damage = 10.0
        self.base_radius = 10.0
        self.base_damage = 10.0
        self.ball_type = "snowball"
        self.skin = "snowball"
        self.alive = True
        self.id = 1
        self.hologram_clones = []

class Hazard:
    def __init__(self, x, y, r, kind):
        self.x = x
        self.y = y
        self.radius = r
        self.kind = kind
        self.active = True
        self.is_disabled_by_flare = False
        self.damage = 0.0

def test_snowball_growth():
    w = MockWorld()
    b = MockBall()
    w.balls.append(b)
    h = Hazard(50, 50, 40, "ice_patch")
    w.arena.hazards.append(h)

    act = Action(b, w)

    assert b.radius == 10.0
    act.execute("idle", 1.0) # move and grow

    assert b.radius > 10.0
    assert b.damage > 10.0
    print(f"Radius: {b.radius}, Damage: {b.damage}")

def test_snowball_no_growth_not_moving():
    w = MockWorld()
    b = MockBall()
    b.vx = 0.0
    b.vy = 0.0
    w.balls.append(b)
    h = Hazard(50, 50, 40, "ice_patch")
    w.arena.hazards.append(h)

    act = Action(b, w)
    act.execute("idle", 1.0)

    assert b.radius == 10.0
    assert b.damage == 10.0

def test_snowball_no_growth_wrong_type():
    w = MockWorld()
    b = MockBall()
    b.ball_type = "normal"
    b.skin = "normal"
    w.balls.append(b)
    h = Hazard(50, 50, 40, "ice_patch")
    w.arena.hazards.append(h)

    act = Action(b, w)
    act.execute("idle", 1.0)

    assert b.radius == 10.0
    assert b.damage == 10.0
