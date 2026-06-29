from ai.perception import Perception

class MockBall:
    def __init__(self, x, y, team=1):
        self.x = x
        self.y = y
        self.team = team
        self.perception_radius = 500

    def has_method(self, name):
        return False

class MockWorld:
    def __init__(self, enemies):
        self.enemies = enemies
        self.arena = None

    def get_nearby_entities(self, ball, radius):
        return {"enemies": self.enemies}

def test_generate_stealth_drone():
    pass

def test_stealth_drone_perception():
    b1 = MockBall(0, 0, 1)
    b2 = MockBall(100, 0, 2)

    b2.has_stealth_drone = True

    world = MockWorld([b2])
    p = Perception(b1, world)

    data = p.scan()
    assert len(data["enemies"]) == 0

    b2.x = 50
    world = MockWorld([b2])
    p = Perception(b1, world)

    data = p.scan()
    assert len(data["enemies"]) == 1
