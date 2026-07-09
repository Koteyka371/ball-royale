import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, radius=10):
        self.id = 1
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = 1000.0
        self.alive = True
        self.ball_type = "base"
        self.zone_immunity_timer = 0.0
        self.status_effects = []

class MockArena:
    def __init__(self):
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 200.0
        self.hazards = []
        self.is_foggy = False
        self.last_tick = 0

    def update_zone(self, tick, delta):
        if tick != self.last_tick:
            self.last_tick = tick
            if self.safe_zone_radius > 0.0:
                self.safe_zone_radius -= 10.0 * delta
                if self.safe_zone_radius < 0.0:
                    self.safe_zone_radius = 0.0

class MockWorld:
    def __init__(self):
        self.tick = 1
        self.arena = MockArena()

def test_safe_zone_damage_outside():
    world = MockWorld()
    # Put ball outside the safe zone
    # Center 500,500, radius 200. So anything > 200 from center is outside.
    ball = MockBall(x=100, y=500) # Dist 400

    action = Action(ball.id, world)
    action.ball = ball

    initial_hp = ball.hp
    action.execute("idle", 0.1)

    assert ball.hp < initial_hp, f"Ball HP should have decreased, got {ball.hp} from {initial_hp}"

def test_safe_zone_damage_inside():
    world = MockWorld()
    # Put ball inside the safe zone
    ball = MockBall(x=500, y=500)

    action = Action(ball.id, world)
    action.ball = ball

    initial_hp = ball.hp
    action.execute("idle", 0.1)

    assert ball.hp == initial_hp, f"Ball HP should not change, got {ball.hp}"
