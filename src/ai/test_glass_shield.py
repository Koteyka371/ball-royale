from ai.action import Action
import pytest

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100
        self.radius = 20.0
        self.alive = True
        self.skill = "deploy_glass_shield"
        self.skill_timer = 0.0
        self.stun_timer = 0.0

class MockHazard:
    def __init__(self, id, x, y, radius, kind, damage):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.duration = 10.0
        self.owner_id = -1

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.events = []
        self.next_id = 100

    def add_event(self, type, data):
        self.events.append((type, data))

def test_deploy_glass_shield():
    ball = MockBall(1, 100, 100)
    world = MockWorld()
    world.balls = [ball]
    action = Action(ball, world)

    action._use_skill()

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "glass_shield"
    assert hazard.owner_id == 1
    assert hazard.radius == 40.0
    assert hazard.damage == 0.0

def test_glass_shield_shatter():
    ball1 = MockBall(1, 100, 100)
    ball2 = MockBall(2, 120, 100) # Within combined radius 20+40 = 60
    world = MockWorld()
    world.balls = [ball1, ball2]

    hazard = MockHazard(99, 100, 100, 40.0, "glass_shield", 0.0)
    hazard.owner_id = 1
    world.arena.hazards.append(hazard)

    action = Action(ball1, world)
    action.execute("attack", 0.1)

    assert len(world.arena.hazards) == 0 # Shattered
    assert ball2.stun_timer >= 3.0 # Stunned
    assert ball1.stun_timer == 0.0 # Owner not stunned (actually stunned because shatter affects all nearby enemies... wait, is the owner an enemy? The action._get_enemies() excludes the active ball)
