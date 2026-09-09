import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.gravity_y = 0.0
        self.seasonal_modifier = ""

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.team = team
        self.alive = True
        self.skill = "throw_time_dilation_grenade"
        self.active_skill = "throw_time_dilation_grenade"
        self.fx = 0.0
        self.fy = 0.0
        self.stutter_timer = 0.0
        self.mass = 1.0

def test_time_dilation_dome_skill():
    world = MockWorld()
    b1 = MockBall(1, 0, 0, 1)
    b2 = MockBall(2, 50, 0, 2)
    b3 = MockBall(3, -50, 0, 1)
    world.balls = [b1, b2, b3]

    action = Action(b1, world)

    # Throw grenade
    action.execute("use_skill", 1.0)
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert getattr(hazard, "kind", "") == "thrown_time_dilation_grenade" or (isinstance(hazard, dict) and hazard.get("kind") == "thrown_time_dilation_grenade")

    hvx = getattr(hazard, "vx", 0) if not isinstance(hazard, dict) else hazard.get("vx", 0)
    assert hvx > 0  # Should travel towards b2

    # Fast forward duration (1.5s)
    action.execute("idle", 1.5)

    # Check if dome was created
    domes = []
    for h in world.arena.hazards:
        kind = getattr(h, "kind", "") if not isinstance(h, dict) else h.get("kind", "")
        if kind == "time_dilation_dome":
            domes.append(h)

    assert len(domes) == 1
    dome = domes[0]
    h_team = getattr(dome, "team", None) if not isinstance(dome, dict) else dome.get("team", None)
    assert h_team == 1

    # Tick inside dome to apply stun to enemies but not allies
    b2.stutter_timer = 0.0
    b3.stutter_timer = 0.0
    # b2 is enemy, should get stutter_timer added by delta. b3 is ally, shouldn't.
    action.execute("idle", 0.5)

    assert b2.stutter_timer > 0.0
    assert b3.stutter_timer == 0.0
