import sys
import pytest
from ai.action import Action
from arena.procedural_arena import ProceduralArena, Hazard

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.hp = 100.0
        self.speed = 2.0
        self.team = "A"
        self.id = 1
        self.is_flying = False

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena()
        self.balls = []
        self.boosters = []
        self.tick = 0

def test_geyser_pressure_and_eruption():
    arena = ProceduralArena()
    geyser = Hazard(1, 100.0, 100.0, 30.0, "geyser", 0.0)
    setattr(geyser, "pressure", 0.0)
    setattr(geyser, "erupting", False)
    setattr(geyser, "erupt_timer", 0.0)
    arena.hazards.append(geyser)
    arena.update_zone(1, 1.0)
    assert getattr(geyser, "pressure") == 20.0
    assert getattr(geyser, "erupting") == False
    arena.update_zone(2, 4.0)
    assert getattr(geyser, "pressure") == 0.0
    assert getattr(geyser, "erupting") == True
    assert getattr(geyser, "erupt_timer") == 2.0
    arena.update_zone(3, 1.0)
    assert getattr(geyser, "erupting") == True
    assert getattr(geyser, "erupt_timer") == 1.0
    arena.update_zone(4, 1.0)
    assert getattr(geyser, "erupting") == False

def test_geyser_launch_ball():
    world = MockWorld()
    ball = MockBall(100.0, 100.0)
    world.balls.append(ball)
    geyser = Hazard(1, 100.0, 100.0, 30.0, "geyser", 0.0)
    setattr(geyser, "pressure", 0.0)
    setattr(geyser, "erupting", True)
    setattr(geyser, "erupt_timer", 2.0)
    world.arena.hazards.append(geyser)
    action = Action(ball, world)
    action.execute("idle", 0.016)
    assert getattr(ball, "is_flying", False) == True
    assert getattr(ball, "fly_timer", 0.0) > 0.0
    assert getattr(ball, "fly_target_x", None) is not None
    assert getattr(ball, "fly_target_y", None) is not None
