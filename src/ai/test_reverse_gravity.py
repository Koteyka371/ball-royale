import pytest
from ai.action import Action

class MockHazard:
    def __init__(self, kind, x, y, radius, damage=0.0):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = damage
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []
        self.is_raining = False
        self.is_foggy = False
        self.safe_zone_radius = float('inf')
        self.safe_zone_center = (0, 0)

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.tick = 0
        self.balls = []

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.alive = True
        self.team = "blue"

    def take_damage(self, amount):
        self.hp -= amount

def test_reverse_gravity_hazard():
    world = MockWorld()
    # Create reverse gravity hazard at 500, 500 with radius 100
    hazard = MockHazard("reverse_gravity", 500.0, 500.0, 100.0, damage=10.0)
    world.arena.hazards.append(hazard)

    # Place ball at 550, 500 (distance 50, inside radius)
    ball = MockBall(550.0, 500.0)
    # Mock attributes required by execute
    ball.speed = 2.0
    ball.base_speed = 2.0
    ball.damage = 10.0
    ball.base_damage = 10.0
    ball.radius = 10.0
    world.balls.append(ball)
    action = Action(ball, world)

    # Need id and cosmetic for Action execution
    ball.id = 1
    ball.cosmetic = "none"
    ball.ball_type = "normal"
    ball.speed = 0.0
    ball.base_speed = 0.0

    # Run _update_hazards logic using execute with idle action
    action.execute('idle', 0.1)

    # Ball should be pushed AWAY from hazard center (dx > 0 so pushed positive x)
    assert ball.x > 550.0, f"Ball was not pushed away, x={ball.x}"

    # Ball should take damage
    assert ball.hp < 100.0, f"Ball did not take damage, hp={ball.hp}"
