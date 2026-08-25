import pytest

class MockBall:
    def __init__(self, x=0.0, y=0.0, traits=None, hp=100.0, alive=True):
        self.id = id(self)
        self.x = x
        self.y = y
        self.traits = traits if traits else []
        self.hp = hp
        self.max_hp = hp
        self.alive = alive
        self.speed = 100.0
        self.base_speed = 100.0
        self.damage = 10.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.team = "A"
        self.shield = 0.0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class MockHazard:
    def __init__(self, x=0.0, y=0.0, kind="poison_cloud", radius=60.0):
        self.id = id(self)
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.active = True
        self.duration = 5.0

class MockArena:
    def __init__(self):
        self.hazards = []
        self.rooms = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_fire_poison_combo():
    from ai.action import Action
    world = MockWorld()

    # Test 1: Fire ignites poison cloud
    fire_ball = MockBall(x=50.0, y=50.0, traits=["fire"])
    poison_cloud = MockHazard(x=50.0, y=50.0, kind="poison_cloud", radius=60.0)
    enemy_ball = MockBall(x=50.0, y=50.0, traits=["water"])

    world.balls = [fire_ball, enemy_ball]
    world.arena.hazards = [poison_cloud]

    action = Action(fire_ball, world)
    action.execute("idle", 0.1)

    assert enemy_ball.hp == 20.0
    assert fire_ball.hp == 20.0
    assert len(world.arena.hazards) == 0
    assert len(world.events) == 1
    assert world.events[0][0] == "combo_explosion"

def test_earth_shield_combo():
    from ai.action import Action
    world = MockWorld()

    # Test 2: Earth unit shields against explosion
    fire_ball = MockBall(x=50.0, y=50.0, traits=["fire"])
    earth_ball = MockBall(x=50.0, y=50.0, traits=["earth"])
    poison_cloud2 = MockHazard(x=50.0, y=50.0, kind="poison_cloud", radius=60.0)

    world.balls = [fire_ball, earth_ball]
    world.arena.hazards = [poison_cloud2]

    action2 = Action(fire_ball, world)
    action2.execute("idle", 0.1)

    assert earth_ball.hp == 100.0
    assert earth_ball.shield == 80.0
    assert len(world.arena.hazards) == 0
