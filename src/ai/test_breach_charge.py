import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, radius=10):
        self.x = x
        self.y = y
        self.radius = radius
        self.breach_charge_active = False

class MockHazard:
    def __init__(self, x=0, y=0, radius=10, kind="bumper"):
        self.emp_disabled_timer = 0.0
        self.emp_disabled_timer = 0.0
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.active = True

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self, arena, boosters=None):
        self.arena = arena
        self.boosters = boosters if boosters is not None else []
        self.balls = []
        self.events = []

def test_breach_charge_collect():
    ball = MockBall()
    arena = MockArena([])
    booster = MockHazard(x=0, y=0, kind="breach_charge_booster")
    world = MockWorld(arena, [booster])

    action = Action(ball, world)
    action._get_boosters = lambda: [booster]
    action._get_enemies = lambda: []
    action._collect_booster(0.1)

    assert ball.breach_charge_active == True
    assert len(world.boosters) == 0

def test_breach_charge_destroy_bumper():
    ball = MockBall(x=10, y=10)
    ball.breach_charge_active = True

    bumper = MockHazard(x=15, y=15, kind="bumper")
    wall = MockHazard(x=100, y=100, kind="breakable_wall")

    arena = MockArena([bumper, wall])
    world = MockWorld(arena)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert len(world.arena.hazards) == 2
    assert bumper.emp_disabled_timer == 15.0
    assert ball.breach_charge_active == False

def test_breach_charge_destroy_wall():
    ball = MockBall(x=100, y=100)
    ball.breach_charge_active = True

    bumper = MockHazard(x=15, y=15, kind="bumper")
    wall = MockHazard(x=105, y=105, kind="breakable_wall")

    arena = MockArena([bumper, wall])
    world = MockWorld(arena)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert len(world.arena.hazards) == 2
    assert wall.emp_disabled_timer == 15.0
    assert ball.breach_charge_active == False

if __name__ == "__main__":
    pytest.main([__file__])
