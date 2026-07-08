from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
    def clamp_position(self, x, y, r=0):
        return x, y, False
    def update_zone(self, tick, delta=0):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick = 0
        self.boosters = []
        self.balls = []

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 200.0
        self.vy = 0.0
        self.radius = 10
        self.hp = 100
        self.alive = True
        self.team = "test"
        self.ball_type = "normal"
        self.max_speed = 200
        self.speed = 200

class Hazard:
    def __init__(self, id, x, y, radius, kind, damage=0):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.lifetime = 10.0

def test_slingshot():
    world = MockWorld()
    bh = Hazard(1, 500, 500, 100, "massive_black_hole", 20.0)
    world.arena.hazards.append(bh)

    ball = MockBall(1, 200, 400)
    world.balls.append(ball)
    world.balls.append(MockBall(2, 0, 0)) # just for loop

    a = Action(ball, world)

    initial_speed = math.hypot(ball.vx, ball.vy)
    print(f"Initial velocity: vx={ball.vx:.1f}, vy={ball.vy:.1f}, speed={initial_speed:.1f}")

    for _ in range(30):
        a.execute("idle", 0.016)
        ball.x += ball.vx * 0.016
        ball.y += ball.vy * 0.016

    final_speed = math.hypot(ball.vx, ball.vy)
    print(f"Final velocity: vx={ball.vx:.1f}, vy={ball.vy:.1f}, speed={final_speed:.1f}")
    print(f"Ball passed center? x={ball.x:.1f}, y={ball.y:.1f}")

    assert final_speed > initial_speed

test_slingshot()
