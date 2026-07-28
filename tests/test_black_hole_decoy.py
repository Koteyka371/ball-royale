import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.events = []
        self.next_id = 1000

class MockArena:
    def __init__(self):
        self.hazards = []
        self.projectiles = []
        self.items = []

class MockEntity:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.active = True
        self.kind = "item"

class MockBall(MockEntity):
    def __init__(self, id, x, y, hp=100):
        super().__init__(id, x, y)
        self.hp = hp
        self.max_hp = hp
        self.stutter_timer = 0.0

def test_black_hole_decoy_spawn():
    world = MockWorld()

    # Decoy that detonates
    decoy = MockBall(2, 100, 100)
    decoy.is_decoy = True
    decoy.decoy_type = "black_hole"
    decoy.owner_id = 1
    decoy.alive = True
    decoy._decoy_exploded = False
    decoy.decoy_timer = 5.0

    # Cause it to explode
    decoy.hp = 0
    world.balls.append(decoy)

    action = Action(decoy, world)
    action.execute("idle", 0.1)

    # Should be dead and exploded
    assert decoy.alive == False
    assert decoy._decoy_exploded == True

    # Should have spawned a decoy_singularity
    hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") == "decoy_singularity"]
    assert len(hazards) == 1
    singularity = hazards[0]
    assert singularity.x == 100
    assert singularity.y == 100
    assert singularity.duration == 2.9
    assert singularity.absorbed_mass == 0.0

def test_black_hole_decoy_pull_and_collapse():
    world = MockWorld()

    class Hazard:
        def __init__(self, id, x, y, r, kind, dmg):
            self.id = id
            self.x = x
            self.y = y
            self.radius = r
            self.kind = kind
            self.damage = dmg
            self.duration = 0.1 # Will collapse this tick
            self.active = True
            self.absorbed_mass = 2.0 # 40 + 2*5 = 50 damage
            self.owner_id = 1

    singularity = Hazard(99, 100, 100, 250, "decoy_singularity", 0)
    world.arena.hazards.append(singularity)

    ball1 = MockBall(1, 100, 100) # Owner, shouldn't be affected
    ball2 = MockBall(3, 150, 100) # Inside radius
    ball3 = MockBall(4, 500, 500) # Outside radius

    world.balls.extend([ball1, ball2, ball3])

    item = MockEntity(10, 110, 100)
    item.kind = "health_pack"
    world.arena.items.append(item)

    action = Action(ball1, world)
    action.execute("idle", 0.1)

    # Check item absorbed
    assert item.active == False

    # Check ball2 pulled
    assert ball2.x < 150 # Moved closer to 100

    # Check collapse damage
    assert singularity.active == False
    assert singularity.duration <= 0
    assert ball2.hp < 100
    assert ball3.hp == 100 # Too far
