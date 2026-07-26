from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.tick = 0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockEntity:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True
        self.radius = 10.0
        self.id = id(self)

class MockBall:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.vx = 5.0
        self.vy = 0.0
        self.ball_type = "player"
        self.badges = []

def test_blink_relic():
    world = MockWorld()
    relic = MockEntity(0, 0, "blink_relic")
    world.boosters.append(relic)
    ball = MockBall()
    world.balls.append(ball)
    action = Action(ball, world)

    # Pickup
    action._collect_booster(0.1)
    assert relic not in world.boosters
    assert getattr(ball, "blink_relic_timer", 0.0) == 15.0
    assert getattr(ball, "max_hp", 100.0) == 70.0
    assert ball.hp <= ball.max_hp

    # Cooldown trigger (initial blink)
    ball.blink_relic_cooldown = 0.0
    initial_x = ball.x
    action.execute("flee", 0.1)
    assert ball.x > initial_x
    assert getattr(ball, "intangible", False) == True

    # Expiration
    ball.blink_relic_timer = 0.1
    action.execute("flee", 0.2)
    assert getattr(ball, "blink_relic_timer", 0.0) == 0.0
    assert getattr(ball, "max_hp", 0.0) == 100.0
