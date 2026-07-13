from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []

class MockArena:
    def __init__(self):
        self.hazards = []

class MockEntity:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

class MockBall:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.perception_radius = 250.0
        self.speed = 2.0
        self.damage = 10.0
        self.ball_type = "test"
        self.badges = []

def test_cursed_relic():
    world = MockWorld()
    relic = MockEntity(0, 0, "cursed_relic")
    world.boosters.append(relic)
    ball = MockBall()
    action = Action(ball, world)

    # Pre-relic stats
    assert ball.perception_radius == 250.0
    assert ball.speed == 2.0
    assert ball.damage == 10.0

    # Collect relic
    action._collect_booster(1.0)

    # Assert relic is removed and stats are changed
    assert relic not in world.boosters
    assert ball.perception_radius == 25.0
    assert ball.speed == 6.0
    assert ball.damage == 30.0
    assert ball.invert_timer == 10.0
    assert ball.cursed_relic_timer == 10.0

    # Tick down
    action.execute("flee", 5.0)
    assert ball.cursed_relic_timer == 5.0
    assert "cursed_relic_survivor" not in ball.badges

    action.execute("flee", 5.0)
    assert ball.cursed_relic_timer == 0.0
    assert ball.perception_radius == 250.0
    assert ball.speed == 2.0
    assert ball.damage == 10.0
    assert "cursed_relic_survivor" in ball.badges
