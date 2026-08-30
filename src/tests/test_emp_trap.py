import pytest
from ai.action import Action

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.x = 0
        self.y = 0
        self.radius = 40.0
        self.team = "B"
        self.owner_id = 2
        self.duration = 20.0
        self.active = True

class MockBall:
    def __init__(self, id, team):
        self.id = id
        self.team = team
        self.x = 0
        self.y = 0
        self.hp = 100
        self.aura_booster_timer = 10.0
        self.vampiric_aura_timer = 10.0
        self.emp_trap_disabled_timer = 0.0
        self.in_aura_nullifier_zone = False
        self.alive = True

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 800
        self.height = 800
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
        self.events = []
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "hazards": self.arena.hazards, "boosters": []}

def test_emp_trap():
    world = MockWorld()
    ball = MockBall(id=1, team="A")
    world.balls.append(ball)

    trap = MockHazard("emp_trap")
    world.arena.hazards.append(trap)

    action = Action(ball, world)

    # 1. First execution processes hazards, triggers trap.
    action.execute("idle", 0.1)

    # The trap logic triggers on tick but the timer doesn't decrement until next tick
    assert ball.emp_trap_disabled_timer == 5.0
    assert ball.aura_booster_timer == 0.0
    assert trap.duration == 0.0
    assert ball.in_aura_nullifier_zone == True

    # Clear out hazards for tick 2
    world.arena.hazards = []

    # 2. Add an aura again and do a normal execute loop
    ball.aura_booster_timer = 10.0
    action.execute("idle", 0.1)

    # Buff should be immediately wiped because timer is active, and timer decrements
    assert ball.aura_booster_timer == 0.0
    assert ball.emp_trap_disabled_timer < 5.0
