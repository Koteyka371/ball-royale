import pytest

def test_chain_immunity_booster_pickup():
    from src.ai.action import Action

    class MockBall:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.vx = 0
            self.vy = 0
            self.speed = 10
            self.radius = 10
            self.alive = True

    class MockBooster:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.kind = "chain_immunity_booster"
            self.active = True

    class MockWorld:
        def __init__(self):
            self.boosters = []

    ball = MockBall()
    booster = MockBooster()
    world = MockWorld()
    world.boosters.append(booster)

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    assert getattr(ball, "chain_immunity_timer", 0.0) == 14.0
    assert len(world.boosters) == 0

def test_chain_immunity_protection():
    from src.ai.action import Action
    class MockBall:
        def __init__(self, id):
            self.id = id
            self.x = 0
            self.y = 0
            self.vx = 0
            self.vy = 0
            self.speed = 10
            self.radius = 10
            self.alive = True
            self.team = "A"
            self.hp = 100
            self.damage = 10

    class MockWorld:
        def __init__(self):
            self.balls = []

    attacker = MockBall(1)
    target1 = MockBall(2)
    target2 = MockBall(3)
    target2.x = 5 # Nearby

    world = MockWorld()
    world.balls = [attacker, target1, target2]

    action = Action(attacker, world)

    # Give target2 immunity
    target2.chain_immunity_timer = 5.0

    # Weather is magnetic storm
    class MockMode:
        def __init__(self):
            self.weather = "magnetic_storm"

    world.game_mode = MockMode()

    # Try basic attack
    action._attempt_damage(attacker, target1)

    # Since chain_chance is 0.5 in magnetic storm, and we want to ensure immunity works,
    # we need a test that directly hits the chain damage code.
    # We will test chain lightning directly instead via skill.

    attacker.skill = "chain_bounce_attack"
    attacker.x = -100
    attacker.y = 0
    target1.x = 0
    target1.team = "B"
    target2.team = "B"

    action.execute("use_skill", 1.0)

    # Target 1 gets hit, but target 2 should be immune and not take damage.
    assert target2.hp == 100
