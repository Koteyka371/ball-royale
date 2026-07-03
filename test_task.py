import math

class Hazard:
    def __init__(self, x, y, radius, damage):
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = damage

class Ball:
    def __init__(self, x, y, hp=100.0):
        self.x = x
        self.y = y
        self.hp = hp

delta = 1.0

hazard = Hazard(100, 100, 50.0, 10.0)
ball = Ball(120, 100)

dx = hazard.x - ball.x
dy = hazard.y - ball.y
dist_sq = dx*dx + dy*dy
eff_radius = hazard.radius * 3.0

if dist_sq > 0.0001 and dist_sq < eff_radius * eff_radius:
    dist = math.sqrt(dist_sq)
    force = (eff_radius / max(10.0, dist)) * 50.0 * delta
    force = min(force, dist * 0.5)

    nx = dx / dist
    ny = dy / dist

    ball.x += nx * force
    ball.y += ny * force

print(ball.x, ball.y)
