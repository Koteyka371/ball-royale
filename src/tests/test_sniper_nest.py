import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self):
        self.x = 0
        self.y = 0
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
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

def test_sniper_nest_active():
    b = MockBall()
    w = MockWorld()
    h = MockHazard('sniper_nest')
    w.arena.hazards.append(h)

    a = Action(b, w)
    a.execute("none", 0.1)

    assert b.in_sniper_nest == True
    assert math.isclose(b.perception_radius, 125.0)
    assert math.isclose(b.damage_multiplier, 1.15)
    assert b.show_sniper_nest_indicator == True

def test_sniper_nest_inactive():
    b = MockBall()
    w = MockWorld()
    h = MockHazard('sniper_nest')
    h.x = 200 # Out of range
    w.arena.hazards.append(h)

    a = Action(b, w)
    a.execute("none", 0.1)

    assert b.in_sniper_nest == False
    assert math.isclose(b.perception_radius, 100.0)
    assert math.isclose(b.damage_multiplier, 1.0)
    assert b.show_sniper_nest_indicator == False

def test_sniper_nest_camouflage_active():
    b = MockBall()
    w = MockWorld()
    h = MockHazard('sniper_nest')
    c = MockHazard('sniper_nest_camouflage')
    w.arena.hazards.extend([h, c])

    a = Action(b, w)
    a.execute("none", 0.1)

    assert b.in_sniper_nest == True
    assert b.show_sniper_nest_indicator == False
    assert c.active == True

def test_sniper_nest_camouflage_destroyed_by_wind():
    b = MockBall()
    w = MockWorld()
    h = MockHazard('sniper_nest')
    c = MockHazard('sniper_nest_camouflage')
    w.arena.hazards.extend([h, c])
    w.arena.weather = "wind"

    a = Action(b, w)
    a.execute("none", 0.1)

    assert c.active == False
    assert b.show_sniper_nest_indicator == True

def test_sniper_nest_camouflage_destroyed_by_explosion():
    b = MockBall()
    w = MockWorld()
    h = MockHazard('sniper_nest')
    c = MockHazard('sniper_nest_camouflage')
    w.arena.hazards.extend([h, c])
    w.events.append(["explosion", {"x": 0.0, "y": 0.0, "radius": 100.0}])

    a = Action(b, w)
    a.execute("none", 0.1)

    assert c.active == False
    assert b.show_sniper_nest_indicator == True

def test_spotter_drone_spawn():
    b = MockBall()
    b.id = 100
    w = MockWorld()
    w.balls = []
    w.next_id = 500
    h = MockHazard('sniper_nest')
    h.x = 0
    h.y = 0
    w.arena.hazards.append(h)

    a = Action(b, w)

    # Needs > 5 seconds in total
    a.execute("none", 5.1)

    # Check that a spotter drone was spawned
    assert len(w.balls) == 1
    drone = w.balls[0]
    assert drone.ball_type == "spotter_drone"
    assert drone.owner_id == b.id

    # Execute again to see perception boost
    a.execute("none", 0.1)
    assert b.perception_radius == b.base_perception_radius * 2.0

    # If drone dies, boost is lost (back to 1.25 nest bonus)
    drone.hp = 0
    a.execute("none", 0.1)
    assert math.isclose(b.perception_radius, b.base_perception_radius * 1.25)
