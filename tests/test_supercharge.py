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

class MockHazard:
    def __init__(self, kind, damage, radius, x, y, hit_targets=False):
        self.id = 1
        self.kind = kind
        self.damage = damage
        self.radius = radius
        self.x = x
        self.y = y
        self.hit_targets = hit_targets

def test_supercharge_robotic():
    ball = MockBall(ball_type="drone", speed=2.0, damage=10.0)
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)

    # Spawn a lightning strike right on top of the ball
    lightning = MockHazard(kind="lightning_strike", damage=50.0, radius=30.0, x=0.0, y=0.0)
    world.arena.hazards.append(lightning)

    delta = 0.1
    action.execute("idle", delta)

    # Lightning strike should deal 50 damage, then drain applies for 0.1s * 5.0 = 0.5 damage
    assert ball.hp == 100.0 - 50.0 - 0.5
    # Ball should be supercharged because it's a "drone", initial 5.0 - delta = 4.9
    assert getattr(ball, "supercharge_timer", 0.0) == 4.9
    assert getattr(ball, "stutter_timer", 0.0) == 0.0

    # Speed and damage should be multiplied by 1.5 in the NEXT tick since it was set in hazard phase
    # Wait, in current tick, hazard phase comes AFTER execute sets speed.
    # So next tick we check it.
    world.arena.hazards = []
    action.execute("idle", delta)

    assert ball.speed == 3.0
    assert ball.damage == 15.0

    # Also check that drain applies again (0.5)
    assert ball.hp == pytest.approx(100.0 - 50.0 - 0.5 - 0.5)
    assert getattr(ball, "supercharge_timer", 0.0) == pytest.approx(4.8)

def test_supercharge_non_robotic():
    ball = MockBall(ball_type="mage", speed=2.0, damage=10.0)
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)

    # Spawn a lightning strike right on top of the ball
    lightning = MockHazard(kind="lightning_strike", damage=50.0, radius=30.0, x=0.0, y=0.0)
    world.arena.hazards.append(lightning)

    delta = 0.1
    action.execute("idle", delta)

    # Lightning strike should deal 50 damage
    assert ball.hp == 50.0
    # Ball should NOT be supercharged because it's a "mage"
    assert getattr(ball, "supercharge_timer", 0.0) == 0.0
    # It should be stunned (1.0 - 0.1 = 0.9)
    assert getattr(ball, "stutter_timer", 0.0) == 0.9

def test_supercharge_metal():
    ball = MockBall(ball_type="knight", speed=2.0, damage=10.0)
    # Give the ball "metal" trait or "armor" trait
    ball.traits = ["metal"]
    world = MockWorld()
    world.balls.append(ball)

    action = Action(ball, world)
    action._base_speed_set = True

    lightning = MockHazard(kind="lightning_strike", damage=50.0, radius=30.0, x=0.0, y=0.0)
    world.arena.hazards.append(lightning)

    delta = 0.1
    action.execute("idle", delta)

    # Ball should get supercharge because of "metal" trait
    assert getattr(ball, "supercharge_timer", 0.0) == pytest.approx(4.9)
    assert getattr(ball, "stutter_timer", 0.0) == 0.0
    # Also speed buff
    assert getattr(ball, "speed_buff_timer", 0.0) == pytest.approx(3.0)
