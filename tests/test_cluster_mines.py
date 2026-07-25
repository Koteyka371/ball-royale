import pytest
from src.ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.next_id = 100

class MockBall:
    def __init__(self, x=0, y=0, id=1, team="red"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100
        self.skill = ""
        self.skill_timer = 0.0
        self.intangible = False
        self.silence_timer = 0.0

class MockHazard:
    def __init__(self, id, x, y, radius, kind, damage):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.duration = 0.0
        self.active = True

def test_deploy_cluster_mines():
    world = MockWorld()
    b1 = MockBall()
    b1.skill = "deploy_cluster_mines"
    world.balls.append(b1)

    action = Action(b1, world)
    action._use_skill()

    assert len(world.arena.hazards) == 5
    for h in world.arena.hazards:
        assert h.kind == "cluster_mine"
        assert h.state == "arming"
        assert h.arming_timer == 3.0

def test_cluster_mine_arming():
    world = MockWorld()
    b1 = MockBall()
    world.balls.append(b1)

    h = MockHazard(1, 0, 0, 20, "cluster_mine", 25)
    h.owner_id = 1
    h.state = "arming"
    h.arming_timer = 1.0
    h.owner_id = b1.id
    world.arena.hazards.append(h)

    action = Action(b1, world)
    action.execute('', 1.5)

    assert h.arming_timer <= 0.0
    assert h.state == "armed"

def test_cluster_mine_proximity_detonation():
    world = MockWorld()
    b1 = MockBall(x=100, y=100) # out of range
    b2 = MockBall(x=0, y=0, id=2) # in range
    world.balls.extend([b1, b2])

    h = MockHazard(1, 0, 0, 20, "cluster_mine", 25)
    h.owner_id = 1
    h.state = "armed"
    h.arming_timer = 0.0
    h.owner_id = b1.id
    world.arena.hazards.append(h)

    action = Action(b2, world) # b2 processes its execute
    action.execute('', 0.1)

    assert h.state == "detonating"

def test_cluster_mine_cascade():
    world = MockWorld()
    b1 = MockBall()
    world.balls.append(b1)

    # Mine 1
    h1 = MockHazard(1, 0, 0, 20, "cluster_mine", 25)
    h1.owner_id = 1
    h1.state = "detonating"
    h1.owner_id = b1.id

    # Mine 2 (in range of explosion)
    h2 = MockHazard(2, 50, 0, 20, "cluster_mine", 25)
    h2.owner_id = 1
    h2.state = "armed"
    h2.owner_id = b1.id

    world.arena.hazards.extend([h1, h2])

    action = Action(b1, world)
    action.execute('', 0.1)

    assert h1.active == False
    assert h2.state == "detonating"
    assert b1.hp < 100

def test_cluster_mine_projectile_detonation():
    world = MockWorld()
    b1 = MockBall()
    world.balls.append(b1)

    # Mine
    h = MockHazard(1, 0, 0, 20, "cluster_mine", 25)
    h.owner_id = 1
    h.state = "armed"
    h.owner_id = b1.id

    # Projectile
    proj = MockHazard(2, 10, 0, 15, "projectile", 10)

    world.arena.hazards.extend([h, proj])

    action = Action(b1, world)
    action.execute('', 0.1)

    assert h.state == "detonating"
