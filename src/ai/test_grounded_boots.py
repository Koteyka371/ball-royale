
from action import Action

def test_grounded_boots():
    class MockBall:
        def __init__(self, x, y, cosmetic="grounded_boots"):
            self.x = x
            self.y = y
            self.vx = 0.0
            self.vy = 0.0
            self.cosmetic = cosmetic
            self.polarity_cooldown = 0
            self.alive = True
            self.team = 1
            self.hp = 100
            self.speed = 2.0
            self.skill = "dash"
    class MockHazard:
        def __init__(self, x, y, kind):
            self.id = 1
            self.x = x
            self.y = y
            self.kind = kind
            self.radius = 50.0
            self.damage = 10.0
            self.active = True
            self.duration = 5.0
            self.lifetime = 5.0
            self.trap_variant = ""

    class MockArena:
        def __init__(self):
            self.hazards = []
            self.safe_zone_center = (500, 500)
            self.safe_zone_radius = 500
            self.width = 1000
            self.height = 1000

    class MockWorld:
        def __init__(self):
            self.balls = []
            self.arena = MockArena()
            self.boosters = []
            self.items = []
            self.tick = 0

    b1 = MockBall(100, 100, "grounded_boots")
    b2 = MockBall(150, 100, "none")
    h_black_hole = MockHazard(100, 110, "black_hole")

    world = MockWorld()

    world.balls = [b1, b2]
    world.arena.hazards = [h_black_hole]

    action_b1 = Action(b1, world)
    action_b2 = Action(b2, world)

    action_b1.execute("flee", 1.0)
    action_b2.execute("flee", 1.0)

    dy_b1 = b1.y - 100
    dy_b2 = b2.y - 100

    assert abs(dy_b1) < 20, f"b1 pulled too much: {dy_b1}"
