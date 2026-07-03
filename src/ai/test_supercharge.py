import pytest
from ai.action import Action
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, id=1, x=0, y=0, ball_type="default"):
        self.id = id
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.hp = 100.0
        self.max_hp = 100.0
        self.speed = 10.0
        self.base_speed = 10.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.alive = True
        self.team = "team_1"
        self.radius = 10.0
        self.traits = []
        self.is_supercharged = False
        self.supercharge_timer = 0.0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

    def update_zone(self, tick, delta=None):
        pass

    def clamp_position(self, x, y, radius=0):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

def test_lightning_strike_supercharge_robotic_ball():
    world = MockWorld()
    # Test with robotic ball
    drone = MockBall(id=1, ball_type="drone")
    world.balls.append(drone)

    # Spawn a lightning strike
    hazard = Hazard(id=1, x=0, y=0, radius=20, kind="lightning_strike", damage=10.0)
    world.arena.hazards.append(hazard)

    action = Action(drone, world)
    # trigger collision via execute (force collision checking)
    action.execute("idle", 0.1)

    # Should have taken damage
    assert drone.hp < 100.0
    # Should be supercharged
    assert drone.supercharge_timer == 4.9
    assert drone.is_supercharged == True
    assert drone.speed == 15.0 # 10 * 1.5
    assert drone.damage == 15.0

def test_lightning_strike_does_not_supercharge_normal_ball():
    world = MockWorld()
    # Test with normal ball
    easy = MockBall(id=1, ball_type="easy")
    world.balls.append(easy)

    hazard = Hazard(id=1, x=0, y=0, radius=20, kind="lightning_strike", damage=10.0)
    world.arena.hazards.append(hazard)

    action = Action(easy, world)
    action.execute("idle", 0.1)

    assert easy.hp < 100.0
    # Should NOT be supercharged
    assert easy.supercharge_timer == 0.0
    assert easy.is_supercharged == False
    assert easy.speed == 10.0

def test_supercharge_timer_and_health_drain():
    world = MockWorld()
    drone = MockBall(id=1, ball_type="drone")
    world.balls.append(drone)

    drone.supercharge_timer = 5.0
    drone.is_supercharged = True
    drone.speed = 15.0
    drone.damage = 15.0

    action = Action(drone, world)

    initial_hp = drone.hp
    # Run _update_skill_timer
    action._update_skill_timer(1.0)

    assert drone.supercharge_timer == 4.0
    assert drone.hp == initial_hp - 10.0
    assert drone.is_supercharged == True
    assert drone.speed == 15.0

    # Run until expiration
    action._update_skill_timer(4.0)

    assert drone.supercharge_timer == 0.0
    assert drone.hp == initial_hp - 50.0
    assert drone.is_supercharged == False
    assert drone.speed == 10.0
    assert drone.damage == 10.0
