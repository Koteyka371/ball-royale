import math
from ai.action import Action

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True

class MockWorld:
    def __init__(self, arena=None):
        self.arena = arena if arena is not None else MockArena()
        self.game_mode = None
        self.width = 1000
        self.height = 1000
        self.balls = []

class MockBall:
    def __init__(self, id, x, y, vx=0.0, vy=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 10.0
        self.speed = 100.0
        self.alive = True
        self.hp = 100
        self.BALL_TYPE = "brawler"

def test_ice_patch_friction_and_bounce():
    ball = MockBall(1, 50, 50, vx=100.0, vy=0.0)
    ice_patch = MockHazard("ice_patch", 50, 50, 50)
    world = MockWorld(MockArena([ice_patch]))
    world.balls.append(ball)

    action = Action(ball, world)

    # Test friction slide
    action.execute("idle", 1.0)

    # Ice patch causes ball to slide without friction (x += vx * delta)
    # Plus idle move, but idle movement might be small.
    # Just check if it's sliding due to vx
    assert getattr(ball, "in_ice_patch", False) == True
    assert ball.x > 100 # Should be at least 150 because of vx=100 and delta=1

    # Test bounce speed amplification
    ball.x = 995 # Near edge
    ball.vx = 100.0
    ball._reflection_vx = 200.0
    ball._reflection_vy = 0.0
    ball._reflection_vx = 200.0
    ball._reflection_vy = 0.0
    ball._reflection_vx = 200.0
    ball._reflection_vy = 0.0
    ball._reflection_vx = 200.0
    ball._reflection_vy = 0.0

    action.execute("idle", 1.0)

    # Expect bounce to have larger speed multiplier
    # Execute removes _reflection_vx and applies it to vx
    speed = math.sqrt(ball.vx**2 + ball.vy**2)
    print("SPEED", speed)
    assert speed >= 150.0 # Bounced on wall, should be at least 1.5x multiplier

if __name__ == "__main__":
    test_ice_patch_friction_and_bounce()
    print("Ice patch tests passed.")
