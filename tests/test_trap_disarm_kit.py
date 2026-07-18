import pytest
from ai.action import Action

class MockBall:
    def __init__(self):
        self.id = 1
        self.team = "team1"
        self.ball_type = "default"
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0

class MockHazard:
    def __init__(self, kind, x, y, invisible=False):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10.0
        self.invisible = invisible
        self.is_invisible = invisible
        self.duration = 10.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []
        self.safe_zone_center = [500, 500]
        self.safe_zone_radius = 500

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.tick = 0
    def get_nearby_entities(self, *args, **kwargs):
        return []
    def _get_boosters(self):
        return self.boosters
        return []

def test_trap_disarm_kit_collection():
    ball = MockBall()
    world = MockWorld()
    action = Action(ball, world)

    kit = MockHazard("trap_disarm_kit", 0.0, 0.0)
    world.boosters.append(kit)

    action._get_boosters = lambda: world.boosters
    action._collect_booster(1.0)

    assert getattr(ball, "trap_disarm_timer", 0.0) == 5.0
    assert kit not in world.boosters

def test_trap_disarm_timer_and_reveal():
    ball = MockBall()
    ball.trap_disarm_timer = 5.0
    world = MockWorld()
    action = Action(ball, world)

    # Invisible trap far away
    trap1 = MockHazard("stun_trap", 100.0, 0.0, invisible=True)
    # Invisible mine very far away (should not be revealed)
    trap2 = MockHazard("sticky_mine", 600.0, 0.0, invisible=True)

    world.arena.hazards.extend([trap1, trap2])

    action.execute("flee", 1.0)

    # Timer decremented
    assert ball.trap_disarm_timer == 4.0

    # Trap 1 should be revealed
    assert not trap1.invisible
    assert not trap1.is_invisible

    # Trap 2 should remain invisible
    assert trap2.invisible

    # Neither trap destroyed
    assert trap1.duration > 0.0
    assert trap2.duration > 0.0

def test_trap_disarm_destruction():
    ball = MockBall()
    ball.trap_disarm_timer = 5.0
    world = MockWorld()
    action = Action(ball, world)

    # Trap very close
    trap = MockHazard("explosive_trap", 5.0, 0.0)
    world.arena.hazards.append(trap)

    action.execute("flee", 1.0)

    # Trap should be destroyed without triggering
    assert trap.duration == 0.0
