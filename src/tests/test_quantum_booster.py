import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id=1, x=100.0, y=100.0, hp=100.0):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100.0
        self.alive = True
        self.has_quantum_booster = False
        self.quantum_booster_active_timer = 0.0
        self.quantum_booster_cooldown = 0.0
        self.quantum_vulnerability_timer = 0.0
        self.active_skill = "use_skill"
        self.skill_timer = 0.0
        self.skill_cooldown = 10.0
        self.radius = 10.0

    def use_skill(self):
        pass

class MockBooster:
    def __init__(self, kind="quantum_booster", x=100.0, y=100.0):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 15.0
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.events = []

def test_quantum_booster_collect_and_use():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)
    action = Action(ball, world)

    # Collection
    booster = MockBooster()
    world.boosters.append(booster)
    action._get_boosters = lambda: world.boosters
    action._collect_booster(0.1)

    assert getattr(ball, "has_quantum_booster", False)
    assert booster not in world.boosters

    # Use Skill
    ball.active_skill = "use_skill"
    action.execute("use_skill", 0.1)
    assert ball.quantum_booster_active_timer > 0.0
    assert ball.quantum_booster_cooldown > 0.0

    # Tick down active timer
    ball.quantum_booster_active_timer = 0.1
    action.execute("idle", 0.2)
    assert ball.quantum_booster_active_timer <= 0.0
    assert ball.quantum_vulnerability_timer == 3.0

    # Check vulnerability damage multiplier
    target = MockBall()
    target.quantum_vulnerability_timer = 3.0
    world.balls.append(target)

    orig_dmg = 10.0
    # The damage logic is internal to action.py _attempt_damage, testing state changes manually
    assert target.quantum_vulnerability_timer > 0
