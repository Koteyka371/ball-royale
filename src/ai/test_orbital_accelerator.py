import pytest
import math
from unittest.mock import MagicMock
from ai.action import Action
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.id = 1
        self.x = x
        self.y = y
        self.team = "test_team"
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.radius = 10.0
        self.base_speed = 200.0
        self.speed = 200.0
        self.damage = 10.0
        self.is_orbiting_accelerator = False
        self.is_flying = False
        self.inventory = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MagicMock()
        self.arena.hazards = []
        self.arena.is_night = False
        self.arena.is_foggy = False
        self.arena.is_eclipse = False
        self.game_mode = MagicMock()
        self.game_mode.name = "default"
        self.arena.safe_zone_center = (500, 500)
        self.arena.safe_zone_radius = 5000
        self.arena.update_zone = MagicMock()
        self.arena.clamp_position = MagicMock(return_value=(10.0, 10.0, False))
        self.width = 1000
        self.height = 1000
        self.arena.clamp_position = MagicMock(return_value=(10.0, 10.0, False))
        self.width = 1000
        self.height = 1000
        self.arena.clamp_position = MagicMock(return_value=(10.0, 10.0, False))
        self.width = 1000
        self.height = 1000
        self.arena.clamp_position = MagicMock(return_value=(10.0, 10.0, False))
        self.width = 1000
        self.height = 1000
        self.arena.safe_zone_center = (500, 500)
        self.arena.safe_zone_radius = 5000
        self.arena.update_zone = MagicMock()
        self.arena.clamp_position = MagicMock(return_value=(10.0, 10.0, False))
        self.width = 1000
        self.height = 1000
        self.arena.clamp_position = MagicMock(return_value=(10.0, 10.0, False))
        self.width = 1000
        self.height = 1000
        self.arena.clamp_position = MagicMock(return_value=(10.0, 10.0, False))
        self.width = 1000
        self.height = 1000
        self.arena.clamp_position = MagicMock(return_value=(10.0, 10.0, False))
        self.width = 1000
        self.height = 1000

def test_orbital_accelerator():
    ball = MockBall(x=10.0, y=10.0)
    world = MockWorld()
    world.balls.append(ball)

    # Place accelerator near the ball
    accelerator = Hazard(id=1, x=0.0, y=0.0, radius=30.0, kind="orbital_accelerator", damage=0.0)
    world.arena.hazards.append(accelerator)

    action = Action(ball, world)

    # Tick 1: Catching the ball
    action.execute("wander", 1/60.0)

    assert ball.is_orbiting_accelerator == True, "Ball should be caught in orbit"
    assert ball.is_flying == False, "Ball should not be flying yet"
    assert hasattr(ball, "orbit_center_x")
    assert hasattr(ball, "orbit_speed")

    # Accelerate and check ejection
    is_ejected = False
    for _ in range(100):
        action.execute("wander", 0.1) # large delta to speed up
        if ball.is_flying:
            is_ejected = True
            break

    assert is_ejected, "Ball should be ejected and flying"
    assert ball.is_orbiting_accelerator == False, "Ball should no longer be orbiting after ejection"
    assert hasattr(ball, "fly_target_x"), "Ball must have a fly target assigned"
    assert hasattr(ball, "fly_timer"), "Ball must have a fly timer assigned"
