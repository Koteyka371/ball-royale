from .action import Action

class MockBall:
    def __init__(self, x=0, y=0, vx=0, vy=0):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 10.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.intangible = False
        self.intangible_timer = 0.0
        self.base_speed = 100.0
        self.base_damage = 10.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self._base_speed_set = True

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True
        self.radius = 10.0

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.safe_zone_center = (0, 0)
        self.safe_zone_radius = 500.0

class MockWorld:
    def __init__(self, balls, arena, boosters):
        self.balls = balls
        self.arena = arena
        self.boosters = boosters

def test_blink_booster_collection():
    ball = MockBall(0, 0, 100, 0)
    booster = MockBooster(10, 0, "blink_booster")
    world = MockWorld([ball], MockArena([booster]), [booster])
    action = Action(ball, world)

    # Workaround to make the AI see the booster and move
    action._get_boosters = lambda: [booster]
    action._get_enemies = lambda: []

    action._collect_booster(0.016)

    assert ball.stamina == 50.0
    assert ball.x > 100.0
    assert booster not in world.boosters
    assert booster not in world.arena.hazards
