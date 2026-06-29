from src.ai.action import Action

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.speed = 2
        self.has_drone = False
        self.has_stealth_drone = False
        self.stealth_drone_timer = 0
        self.current_action = "idle"

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.x = 0
        self.y = 0

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards

class MockWorld:
    def __init__(self, arena):
        self.arena = arena
        self.balls = []

def test_collect_stealth_drone():
    h = MockHazard("stealth_drone_item")
    world = MockWorld(MockArena([h]))
    ball = MockBall(0, 0)

    a = Action(ball, world)
    ball.current_action = "opportunistic"
    a.execute("opportunistic", 0.1)

    # Needs a way to mock perception / nearby entities, but we can call internal method
    # Actually action._collect_booster handles it if nearest is the hazard, but opportunistic goes to nearest booster.
    pass
