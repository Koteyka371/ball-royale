from ai.action import Action

class MockBall:
    def __init__(self):
        self.id = 1
        self.hp = 100
        self.alive = True
        self.perception_radius = 250.0
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.team = "player"
        self.glitch_timer = 0.0
        self.ball_type = "basic"
        self.speed = 100
        self.base_speed = 100
        self.radius = 15.0
        self.silence_timer = 0.0
        self.is_blinded = False

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0
        self.active = True

class MockHazard:
    def __init__(self):
        self.id = 100
        self.kind = "trap"
        self.trap_variant = "blackout"
        self.owner_id = 2
        self.x = 0
        self.y = 0
        self.radius = 15.0
        self.damage = 0.0
        self.duration = 5.0
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = [MockHazard()]
        self.width = 1000
        self.height = 1000
    def clamp_position(self, x, y, radius):
        return x, y, False
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
    def _collect_booster(self, ball, booster):
        pass

def test_blackout_trap_effects():
    ball = MockBall()
    world = MockWorld()
    world.balls = [ball]
    booster = MockBooster(0, 0, "speed_booster")
    world.boosters = [booster]

    action = Action(ball, world)

    # Run a tick
    action.execute("idle", 0.1)

    # Verify trap took effect
    assert getattr(ball, "is_blinded", False) == True
    assert getattr(ball, "perception_radius") == 0.0
    assert getattr(ball, "silence_timer", 0.0) >= 5.0
    assert world.arena.hazards[0].duration == 0.0

    # Try to collect booster while blinded
    action._get_boosters = lambda: world.boosters
    action._collect_booster(0.1)

    # Booster should still be there because we can't collect it
    assert len(world.boosters) == 1
