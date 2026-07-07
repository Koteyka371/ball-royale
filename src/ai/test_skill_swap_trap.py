import pytest
from ai.action import Action

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.duration = 10.0
        self.x = 100
        self.y = 100
        self.radius = 20
        self.damage = 0

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000
    def update_zone(self, tick, delta=None):
        pass
    def clamp_position(self, x, y, radius=0):
        return (x, y, False)

class MockEventList(list):
    pass

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.events = MockEventList()
        self.tick = 123
        self.time = 0.0

class MockBall:
    def __init__(self, id, x, y, active_skill=None, inventory=None):
        self.id = id
        self.x = x
        self.y = y
        self.active_skill = active_skill
        self.inventory = inventory or []
        self.radius = 10
        self.speed = 0
        self.alive = True
        self.is_decoy = False

def test_skill_swap_trap():
    trap = MockHazard("skill_swap_trap")
    arena = MockArena([trap])
    my_ball = MockBall(1, 100, 100, "dash", ["item1"])
    other_ball = MockBall(2, 200, 200, "shield", ["item2"])
    world = MockWorld(arena, [my_ball, other_ball])
    action = Action(my_ball, world)

    # Trigger the trap
    action.execute("none", 0.0)

    assert my_ball.active_skill == "shield"
    assert my_ball.inventory == ["item2"]
    assert other_ball.active_skill == "dash"
    assert other_ball.inventory == ["item1"]
    assert trap.duration == 0.0

    # Now simulate time passing
    world.time = 15.0

    action.execute("none", 0.0)

    # Should revert
    assert my_ball.active_skill == "dash"
    assert my_ball.inventory == ["item1"]
