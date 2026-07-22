import pytest

class MockBall:
    def __init__(self):
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.speed = 10.0
        self.damage = 10.0
        self.max_stamina_timer = 0.0
        self.overflow_active = False
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.id = 1
        self.alive = True
        self.team = "A"

class MockWorld:
    def __init__(self):
        self.balls = []

    def _deal_damage(self, attacker, target, dmg=None):
        pass

def test_overflow_state():
    from ai.action import Action
    ball = MockBall()
    world = MockWorld()
    world.balls = [ball]
    action = Action(ball, world)

    # Need to give the world an arena with boundaries to prevent more errors
    class MockArena:
        def __init__(self):
            self.hazards = []
            self.width = 1000
            self.height = 1000
    world.arena = MockArena()

    # Tick for 5 seconds at max stamina
    action.execute("idle", 5.0)

    assert getattr(ball, "overflow_active", False) == True

    # 20% speed boost should be applied if it had some logic, but wait, action execute loops and multiplies speed on each tick.
    # actually, action.execute just sets `self.ball.speed *= 1.2` each tick? Let's check!
    # Ah, action execute recalculates speed or multiplies it? It multiplies `self.ball.speed` but doesn't it compound?
    # Usually in action.py: `self.ball.speed = getattr(self.ball, "base_speed", 100.0)`

def test_overflow_damage_reduction():
    from ai.action import Action
    ball = MockBall()
    target = MockBall()
    target.overflow_active = True

    world = MockWorld()
    world.balls = [ball, target]
    action = Action(ball, world)

    attacker = MockBall()
    attacker.damage = 100.0

    # Test damage reduction logic in _attempt_damage
    class InterceptAction(Action):
        def _attempt_damage_internal(self, attacker, target):
            self.intercepted_dmg = attacker.damage

    iaction = InterceptAction(ball, world)
    iaction._attempt_damage(attacker, target)

    assert iaction.intercepted_dmg == pytest.approx(85.0)
    assert attacker.damage == pytest.approx(100.0)
