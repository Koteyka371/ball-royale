from ai.perception import Perception

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.perception_radius = 500.0

class MockHazard:
    def __init__(self, id, x, y, radius, kind):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.active = True

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.is_night = False
        self.is_foggy = False
        self.is_raining = False
        self.is_sandstorming = False
        self.is_snowing = False

class MockWorld:
    def __init__(self, arena, enemies):
        self.arena = arena
        self.enemies = enemies

    def get_nearby_entities(self, ball, radius):
        return {"enemies": self.enemies}

def test_breakable_wall_blocks_vision():
    ball = MockBall(0, 0)
    enemy = MockBall(100, 0)

    # Wall is in between
    wall = MockHazard(1, 50, 0, 10, "breakable_wall")
    world = MockWorld(MockArena([wall]), [enemy])

    p = Perception(ball, world)
    data = p.scan()

    # Vision should be blocked
    assert len(data["enemies"]) == 0

def test_breakable_wall_does_not_block_clear_vision():
    ball = MockBall(0, 0)
    enemy = MockBall(100, 100)

    # Wall is out of the way
    wall = MockHazard(1, 50, 0, 10, "breakable_wall")
    world = MockWorld(MockArena([wall]), [enemy])

    p = Perception(ball, world)
    data = p.scan()

    # Vision should NOT be blocked
    assert len(data["enemies"]) == 1
