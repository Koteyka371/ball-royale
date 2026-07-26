from ai.action import Action
import pytest

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []

class MockArena:
    def __init__(self):
        self.hazards = []

class MockEntity:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.radius = 10.0
        self.perception_radius = 250.0
        self.speed = 2.0
        self.damage = 10.0
        self.ball_type = "test"
        self.badges = []
        self.hp = 100.0
        self.max_hp = 100.0

def test_cursed_relic_health_drain_and_heal():
    world = MockWorld()
    relic = MockEntity(0, 0, "cursed_relic")
    world.boosters.append(relic)
    ball = MockBall()
    enemy = MockBall(x=50.0, y=50.0) # Within 150 aura
    enemy.hp = 100.0
    world.balls = [ball, enemy]

    action = Action(ball, world)

    # Collect relic
    action._collect_booster(1.0)

    # Tick down
    action.execute("flee", 1.0)

    # Check HP drain and heal
    # ball hp changes: -5.0 * 1.0 = -5.0
    # enemy hp changes: -10.0 * 1.0 = -10.0
    # ball heals: 10.0 * 0.5 = 5.0
    # total ball hp: 100.0 - 5.0 + 5.0 = 100.0

    assert enemy.hp == 90.0
    assert ball.hp == 100.0

    # Test far enemy (out of range)
    far_enemy = MockBall(x=200.0, y=200.0)
    far_enemy.hp = 100.0
    world.balls = [ball, far_enemy]

    action.execute("flee", 1.0)

    # Far enemy should not be damaged
    assert far_enemy.hp == 100.0
    # Ball should only drain, no healing (because no enemy damaged)
    assert ball.hp == 95.0
