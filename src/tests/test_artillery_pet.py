from ai.action import Action
import math

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.has_pet = False
        self.pet_type = ""
        self.pet_cooldown = 0.0

class MockHazard:
    def __init__(self, id, x, y, kind, owner_id=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True
        self.owner_id = owner_id

class MockItem:
    def __init__(self, id, x, y, kind):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []
        self.items = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.projectiles = []
        self.arena = MockArena()
        self.boosters = []

def test_artillery_pet_collection():
    b = MockBall(1, 0, 0, 1)
    w = MockWorld()
    item = MockItem(1, 5, 5, "artillery_pet_item")
    w.arena.items.append(item)
    w.boosters.append(item)
    w.balls.append(b)

    action = Action(b, w)
    action._collect_booster(0.1)

    assert b.has_pet
    assert b.pet_type == "artillery"
    assert b.pet_cooldown == 0.0
    assert len(w.arena.hazards) == 1
    assert w.arena.hazards[0].kind == "pet"
    assert w.arena.hazards[0].owner_id == b.id

def test_artillery_pet_logic_distant_enemy():
    b = MockBall(1, 0, 0, 1)
    b.has_pet = True
    b.pet_type = "artillery"
    b.pet_cooldown = 0.0

    w = MockWorld()
    w.balls.append(b)

    # Pet object
    pet = MockHazard(2, -10, -10, "pet", 1)
    w.arena.hazards.append(pet)

    # Distant enemy (distance > 200, i.e., dist_sq > 40000)
    enemy = MockBall(3, 300, 0, 2)
    w.balls.append(enemy)

    action = Action(b, w)

    # We will simulate the execution logic, which includes _apply_hazards internally or just call the snippet
    # In action.py, pet update logic is in _apply_hazards? No, it's directly in `execute` loop but for this
    # we can call action.execute() but since it needs target acquisition and other things,
    # it's better to just mock up enough state.
    # To avoid Action.execute failures with missing mock attributes, let's just initialize the missing ones.

    b.vx = 0
    b.vy = 0
    b.mass = 1.0
    enemy.vx = 0
    enemy.vy = 0
    enemy.mass = 1.0
    b.action = "idle"
    enemy.action = "idle"

    # Action execute
    action.execute("move", 0.1)

    # Pet logic triggers after stutter timer block in execute
    assert len(w.projectiles) == 1
    p = w.projectiles[0]
    assert p.kind == "artillery"
    assert p.owner_id == b.id
    assert p.damage == 30.0
    assert p.x == -10
    assert p.y == -10
    assert abs(b.pet_cooldown - 3.0) < 0.01

def test_artillery_pet_logic_close_enemy():
    b = MockBall(1, 0, 0, 1)
    b.has_pet = True
    b.pet_type = "artillery"
    b.pet_cooldown = 0.0

    w = MockWorld()
    w.balls.append(b)

    pet = MockHazard(2, -10, -10, "pet", 1)
    w.arena.hazards.append(pet)

    # Close enemy (distance <= 200)
    enemy = MockBall(3, 100, 0, 2)
    w.balls.append(enemy)

    b.vx = 0
    b.vy = 0
    b.mass = 1.0
    b.action = "idle"
    enemy.vx = 0
    enemy.vy = 0
    enemy.mass = 1.0
    enemy.action = "idle"

    action = Action(b, w)
    action.execute("move", 0.1)

    assert len(w.projectiles) == 0
    assert b.pet_cooldown == 0.0
