import pytest
from ai.game_modes import PhysicsAnomalyMode
from ai.action import Action
from arena.procedural_arena import Hazard

class MockWorld:
    def __init__(self):
        class Arena:
            def __init__(self):
                self.hazards = []
                self.width = 2000.0
                self.height = 2000.0
        self.arena = Arena()
        self.events = []

class MockBall:
    def __init__(self, id, x, y, vx, vy):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True
        self.ball_type = "normal"
        self.hp = 100
        self.max_hp = 100
        self.team = "team1"
        self.radius = 10.0
        self.damage = 10.0
        self.took_damage = False

    def take_damage(self, amount):
        self.took_damage = True

def test_physics_anomaly_mode_setup():
    mode = PhysicsAnomalyMode()
    world = MockWorld()
    balls = [MockBall(1, 100, 100, 0, 0)]

    mode.setup(world, balls)

    assert len(world.arena.hazards) == 1
    anomaly = world.arena.hazards[0]
    assert anomaly.kind == "physics_anomaly"
    assert anomaly.x == 1000.0
    assert anomaly.y == 1000.0
    assert anomaly.radius == 100.0

def test_physics_anomaly_mode_tick_movement():
    mode = PhysicsAnomalyMode()
    world = MockWorld()

    b1 = MockBall(1, 500, 500, 10, 10)
    b2 = MockBall(2, 1500, 1500, 10, 10)
    b3 = MockBall(3, 100, 100, 0, 0)

    balls = [b1, b2, b3]

    mode.setup(world, balls)
    mode.tick(world, balls, 1.0)

    assert b1.vx > 10.0
    assert b1.vy > 10.0

    assert b2.vx < 10.0
    assert b2.vy < 10.0

    assert b3.vx == 0
    assert b3.vy == 0

def test_physics_anomaly_projectile_curve():
    world = MockWorld()

    barrier = Hazard(id=1, x=500, y=500, radius=40, kind="energy_barrier", damage=0)
    barrier.team = "enemy"
    world.arena.hazards.append(barrier)

    action = Action(1, world)
    action.ball = MockBall(1, 400, 400, 0, 0)

    attacker = action.ball
    target = MockBall(2, 600, 600, 0, 0)
    target.team = "enemy"

    # We will test using the visual event added when a barrier blocks a shot
    action._attempt_damage(attacker, target)

    assert len(world.events) == 1
    assert world.events[0]['data']['type'] == 'shield_block'

    # Add physics anomaly to the world
    anomaly = Hazard(id=2, x=1000, y=1000, radius=100, kind="physics_anomaly", damage=0)
    world.arena.hazards.append(anomaly)
    world.events.clear()

    # Now try again
    action._attempt_damage(attacker, target)

    # It should curve around, not be blocked, so no visual event
    assert len(world.events) == 0
