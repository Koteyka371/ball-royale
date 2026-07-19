import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.boundary_states = {"top": "absorptive", "bottom": "absorptive", "left": "absorptive", "right": "absorptive"}
        self.hazards = []

    def clamp_position(self, x, y, r):
        # We manually clamp in tests sometimes, let's just use boundary collision manually
        return x, y, False

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.arena = MockArena()
        self.game_mode = None
        self.events = []

class MockBall:
    def __init__(self):
        self.id = 1
        self.ball_type = "warrior"
        self.x = 0
        self.y = 500
        self.vx = -100
        self.vy = 0
        self.radius = 10.0
        self.hp = 100
        self.speed = 100.0
        self._reflection_vx = 0.0
        self._reflection_vy = 0.0

def test_absorptive_walls():
    world = MockWorld()
    ball = MockBall()
    action = Action(ball, world)

    def override_clamp():
        # Force a bounce on the left wall
        if action.ball.x <= action.ball.radius:
            action.ball.x = action.ball.radius
            return True
        return False

    action._clamp_position = override_clamp
    action.execute("idle", 0.016)

    # Check if a defensive shield was spawned
    assert len(world.arena.hazards) > 0
    shield = world.arena.hazards[-1]
    assert getattr(shield, "kind", "") == "defensive_shield"
    assert getattr(shield, "radius", 0) == 50.0

    # speed was 100.0. Absorptive sets it to 100 * 0.75 = 75.0
    new_speed = math.sqrt(ball.vx**2 + ball.vy**2)
    assert 70.0 < new_speed < 80.0
