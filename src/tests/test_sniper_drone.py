import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self, team="blue", x=0, y=0):
        self.team = team
        self.x = x
        self.y = y
        self.radius = 10.0
        self.perception_radius = 100.0
        self.base_perception_radius = 100.0
        self.in_sniper_nest = False
        self.damage_multiplier = 1.0
        self.show_sniper_nest_indicator = False

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.x = 0
        self.y = 0
        self.radius = 50.0
        self.sniper_drone_active = False
        self.sniper_drone_timer = 0.0
        self.sniper_drone_angle = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []

def test_sniper_drone_spawn_and_vision():
    b = MockBall()
    w = MockWorld()
    h = MockHazard('sniper_nest')
    h.sniper_drone_timer = 0.1
    w.arena.hazards.append(h)
    w.balls.append(b)

    a = Action(b, w)
    a.execute("none", 0.1)

    assert h.sniper_drone_active == True
    assert b.perception_radius == 800.0

def test_sniper_drone_destroyed_by_enemy():
    b = MockBall(team="blue")
    enemy = MockBall(team="red", x=75.0, y=0.0) # drone orbits at 50 * 1.5 = 75

    w = MockWorld()
    h = MockHazard('sniper_nest')
    h.sniper_drone_active = True
    h.sniper_drone_angle = 0.0
    w.arena.hazards.append(h)
    w.balls.extend([b, enemy])

    a = Action(b, w)
    a.execute("none", 0.1)

    assert h.sniper_drone_active == False
    assert h.sniper_drone_timer == 10.0
