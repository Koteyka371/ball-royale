import math
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.tick = 1
        self.arena = type('MockArena', (), {'hazards': [], 'weather': ''})()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.mass = 1.0
        self.speed = 100.0
        self.team = "A"
        self.ball_type = "normal"

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True
        self.is_disabled_by_flare = False

world = MockWorld()
ball = MockBall(1, 0, 0)
trap = MockHazard("shrink_ray_trap", 0, 0, 10.0)
world.arena.hazards.append(trap)

action = Action(ball, world)
action._resolve_collisions()
print(f"dist: {math.sqrt((ball.x - trap.x)**2 + (ball.y - trap.y)**2)}")
print(f"threshold: {ball.radius + trap.radius}")
print(f"radius: {ball.radius}, mass: {ball.mass}, speed: {ball.speed}, active: {trap.active}")
