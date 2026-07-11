import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 800
        self.height = 600

    def update_zone(self, tick, delta=None):
        pass

    def clamp_position(self, x, y, radius=0):
        return x, y, False

class MockBall:
    def __init__(self, ball_type, hp=100.0, speed=2.0, damage=10.0, x=0.0, y=0.0):
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.damage = damage
        self.x = x
        self.y = y
        self.id = 1
        self.team = "test_team"
        self.alive = True
        self.radius = 10.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.supercharge_timer = 0.0
        self.stutter_timer = 0.0
        self.base_speed = speed
        self.base_damage = damage

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

    def get_nearby_entities(self, entity, radius):
        enemies = [b for b in self.balls if b.team != entity.team]
        return {'enemies': enemies}

class MockHazard:
    def __init__(self, kind, damage, radius, x, y, hit_targets=False):
        self.id = 1
        self.kind = kind
        self.damage = damage
        self.radius = radius
        self.x = x
        self.y = y
        self.hit_targets = hit_targets

def test_overcharged():
    ball = MockBall(ball_type="lightning_rod", speed=2.0, damage=10.0)
    enemy = MockBall(ball_type="mage", speed=2.0, damage=10.0)
    enemy.team = "enemy_team"
    enemy.x = 50.0 # Within 150 radius

    world = MockWorld()
    world.balls.append(ball)
    world.balls.append(enemy)

    action = Action(ball, world)

    # Strike 1
    lightning = MockHazard(kind="lightning_strike", damage=50.0, radius=30.0, x=0.0, y=0.0)
    world.arena.hazards = [lightning]
    action.execute("idle", 0.1)

    assert getattr(ball, "supercharge_timer", 0.0) == pytest.approx(4.9)
    assert getattr(ball, "overcharged_timer", 0.0) == 0.0

    # Strike 2
    lightning2 = MockHazard(kind="lightning_strike", damage=50.0, radius=30.0, x=0.0, y=0.0)
    world.arena.hazards = [lightning2]
    action.execute("idle", 0.1)

    # Strike 3
    lightning3 = MockHazard(kind="lightning_strike", damage=50.0, radius=30.0, x=0.0, y=0.0)
    world.arena.hazards = [lightning3]
    action.execute("idle", 0.1)

    # After 3 strikes it should be overcharged
    assert getattr(ball, "overcharged_timer", 0.0) > 0.0

    world.arena.hazards = []
    action.execute("idle", 0.1)
    assert ball.speed == pytest.approx(2.0 * 1.5 * 1.3)

    # Wait for zap
    for _ in range(10):
        action.execute("idle", 0.1)

    # Zap should happen
    assert enemy.hp < 100.0

print("Test written")
