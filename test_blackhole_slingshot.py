from src.ai.action import Action

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
        self.vx = 0.0
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

import math

def test_slingshot():
    world = MockWorld()
    world.arena = MockArena()
    world.balls = []

    # Place a massive black hole
    bh = Hazard(1, 500, 500, 100, "massive_black_hole", 20.0)
    bh.lifetime = 10.0 # High lifetime for stronger pull
    world.arena.hazards.append(bh)

    # Place ball far away but moving fast orthogonally
    ball = MockBall(1, 400, 200)
    ball.vx = 0
    ball.vy = 200
    world.balls.append(ball)
    world.balls.append(ball) # Just making sure it iterates

    a = Action(ball, world)

    for _ in range(10):
        # We simulate manually since we don't need a strategy just for pulling
        ball.x += ball.vx * 0.016
        ball.y += ball.vy * 0.016
        a.execute("idle", 0.016)

    print("Final speed:", math.hypot(ball.vx, ball.vy))
    print(f"Final pos: ({ball.x}, {ball.y})")

test_slingshot()
