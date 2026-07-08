def test_bounce_pad_push():
    from ai.action import Action

    class MockBall:
        def __init__(self):
            self.id = 1
            self.x = 100.0
            self.y = 100.0
            self.vx = 0.0
            self.vy = 0.0
            self.radius = 15.0
            self.mass = 1.0
            self.alive = True
            self.hp = 100.0
            self.team = "A"
            self.status_effects = {}
            self.is_stunned = False

    class MockHazard:
        def __init__(self):
            self.id = 101
            self.x = 100.0
            self.y = 105.0 # slightly offset to create a direction
            self.vx = 0.0
            self.vy = 0.0
            self.radius = 50.0
            self.kind = "bounce_pad"
            self.damage = 0.0

    class MockArena:
        def __init__(self):
            self.hazards = [MockHazard()]
            self.boosters = []
            self.width = 1000
            self.height = 1000
        def update_zone(self, tick, delta=None):
            pass
        def clamp_position(self, x, y, radius=0):
            return x, y, False

    class MockWorld:
        def __init__(self):
            self.balls = []
            self.arena = MockArena()
            self.boosters = []
            self.leaderboard_manager = type('LBM', (), {'data': {'current_season': 0}})()

    ball = MockBall()
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)
    # Don't use a strategy that moves the ball automatically
    action.execute(strategy='idle', delta=0.1)

    # In action.py, the bounce pad logic sets vx and vy to nx * 1500.0 and ny * 1500.0
    assert abs(ball.vy) > 100.0, "Bounce pad should severely push the ball in Y direction"
    assert ball.y != 100.0, "Bounce pad should bump position"
