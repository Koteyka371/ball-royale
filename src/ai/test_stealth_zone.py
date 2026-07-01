import pytest
from ai.perception import Perception

class MockBall:
    def __init__(self, x=0, y=0, team="red", ball_type="brawler", id=1):
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.id = id
        self.hp = 100
        self.has_drone = False
        self.perception_score = 10
        self.has_stealth_drone = False
        self.shadow_booster_timer = 0

    def has_method(self, name):
        return False

    def get_meta(self, name):
        return None

class MockHazard:
    def __init__(self, kind="stealth_zone", x=0, y=0, radius=50, id=1):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.id = id
        self.active = True

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards or []
        self.is_foggy = False
        self.is_raining = False
        self.is_sandstorming = False
        self.is_snowing = False

class MockWorld:
    def __init__(self, arena=None):
        self.arena = arena
        self.coach_strategy = None
        self.entities = {"enemies": [], "allies": [], "boosters": [], "traps": []}

    def get_nearby_entities(self, ball, radius):
        return self.entities

def test_stealth_zone():
    my_ball = MockBall(x=0, y=0, id=1)
    enemy_ball = MockBall(x=100, y=0, id=2)
    world = MockWorld(arena=MockArena(hazards=[]))
    world.entities["enemies"] = [enemy_ball]

    perception = Perception(my_ball, world)

    # 1. No stealth zone - can see enemy
    data = perception.scan()
    assert len(data["enemies"]) == 1

    # 2. Enemy is in stealth zone, I am not - cannot see enemy
    sz1 = MockHazard("stealth_zone", x=100, y=0, radius=50, id=101)
    world.arena.hazards = [sz1]
    data = perception.scan()
    assert len(data["enemies"]) == 0

    # 3. Both are in the SAME stealth zone - can see enemy
    my_ball.x = 80
    data = perception.scan()
    assert len(data["enemies"]) == 1

    # 4. I am in a stealth zone, enemy is in DIFFERENT stealth zone - cannot see enemy
    sz2 = MockHazard("stealth_zone", x=0, y=0, radius=50, id=102)
    world.arena.hazards = [sz1, sz2]
    my_ball.x = 0
    data = perception.scan()
    assert len(data["enemies"]) == 0

    # 5. I am in a stealth zone, enemy is NOT in stealth zone - can see enemy
    world.arena.hazards = [sz2]
    data = perception.scan()
    assert len(data["enemies"]) == 1
