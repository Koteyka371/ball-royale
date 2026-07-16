from unittest.mock import MagicMock
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
            self.polarity_cooldown = 0
            self.skill = "dash"
            self.radius = 10.0
            self.wall_stick_timer = 0.0
            self.zone_immunity_timer = 0.0
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

    b1 = MockBall(100, 100, "grounded_boots")
    b2 = MockBall(100, 100, "none")
    h_black_hole = MockHazard(100, 110, "black_hole")

    class MockArena:
        def __init__(self):
            self.width = 1000.0
            self.height = 1000.0
            self.safe_zone_center = (500, 500)
            self.safe_zone_radius = 1000
            self.damage_per_second = 10.0
            self.hazards = []
            self.weather = "clear"
        def update_zone(self, tick, delta):
            pass
        def clamp_position(self, x, y, r):
            return (x, y, False)
    class MockWorld:
        def __init__(self):
            self.balls = []
            self.arena = MockArena()
            self.boosters = []
            self.items = []
            self.tick = 1
    world = MockWorld()

    world.balls = [b1, b2]
    world.arena.hazards = [h_black_hole]
    world.boosters = []
    world.items = []

    action_b1 = Action(b1, world)
    action_b2 = Action(b2, world)
    action_b1.ball.polarity_cooldown = 0
    action_b2.ball.polarity_cooldown = 0

    # Tick to process pull
    action_b1.execute("flee", 1.0)
    action_b2.execute("flee", 1.0)

    dy_b1 = b1.y - 100
    dy_b2 = b2.y - 100

    assert abs(dy_b1) < abs(dy_b2), f"b1 pulled too much: {dy_b1}"
