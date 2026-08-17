from ai.action import Action

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 100.0
        self.y = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.speed = 100.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = "team1"
        self.mass = 1.0

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.x = 100.0
        self.y = 100.0
        self.radius = 15.0
        self.active = True
        self.damage = 10.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000

def test_pinball_booster():
    ball = MockBall()
    world = MockWorld()
    world.balls.append(ball)

    booster = MockHazard("pinball_booster")
    world.boosters.append(booster)

    action = Action(ball, world)
    action._collect_booster(0.1)

    assert getattr(ball, "pinball_booster_timer", 0.0) > 0.0
    assert getattr(ball, "is_frictionless", False) == True
    assert getattr(ball, "skill_silenced", False) == True
    assert getattr(ball, "knockback_multiplier_outgoing", 1.0) == 2.0

    # Tick timer
    ball.pinball_booster_timer = 0.05
    action.execute("idle", 0.1)

    assert getattr(ball, "pinball_booster_timer", 0.0) == 0.0
    assert getattr(ball, "is_frictionless", False) == False
    assert getattr(ball, "skill_silenced", False) == False
    assert getattr(ball, "knockback_multiplier_outgoing", 1.0) == 1.0
