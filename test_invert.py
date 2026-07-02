import math

class MockBall:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.speed = 2.0
        self.invert_timer = 5.0
        self.radius = 10.0
        self.team = 1
        self.alive = True
        self.ball_type = "normal"
        self.hp = 100
        self.max_hp = 100

class MockTarget:
    def __init__(self):
        self.x = 100.0
        self.y = 0.0
        self.radius = 10.0

ball = MockBall()
target = MockTarget()

def chase(ball, target, delta):
    dx = target.x - ball.x
    dy = target.y - ball.y
    dist = math.sqrt(dx*dx + dy*dy)
    if dist > 0:
        nx = dx / dist
        ny = dy / dist

        # simulated logic
        speed = ball.speed
        if getattr(ball, "invert_timer", 0.0) > 0:
            speed = -speed

        step = speed * delta * 60.0
        print(f"step={step}, min(step, dist)={min(step, dist)}")
        ball.x += nx * min(step, dist)
        ball.y += ny * min(step, dist)

print("Before:", ball.x, ball.y)
chase(ball, target, 1/60.0)
print("After:", ball.x, ball.y)
