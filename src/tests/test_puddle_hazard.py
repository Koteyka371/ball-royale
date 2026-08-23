from ai.game_modes import GameMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y, b_type="normal"):
        self.x = x
        self.y = y
        self.radius = 15.0
        self.alive = True
        self.ball_type = b_type
        self.traits = []
        self.speed = 100.0
        self.base_speed = 100.0
        self.hp = 100.0

class MockHazard:
    def __init__(self, x, y, r, kind):
        self.x = x
        self.y = y
        self.radius = r
        self.kind = kind

def test_puddle_slows_balls():
    mode = GameMode()
    world = MockWorld()
    b = MockBall(0,0)
    world.arena.hazards.append(MockHazard(0, 0, 50, "puddle"))
    mode.apply_dynamic_traits(world, [b], 1.0)
    assert b.speed == 70.0
    assert getattr(b, "in_puddle", False) is True

    b.x = 100
    b.y = 100
    mode.apply_dynamic_traits(world, [b], 1.0)
    assert b.speed == 100.0
    assert getattr(b, "in_puddle", False) is False

def test_puddle_slows_multiple_balls():
    mode = GameMode()
    world = MockWorld()
    b1 = MockBall(0,0)
    b2 = MockBall(0,0)
    b3 = MockBall(100,100)
    world.arena.hazards.append(MockHazard(0, 0, 50, "puddle"))
    mode.apply_dynamic_traits(world, [b1, b2, b3], 1.0)
    assert b1.speed == 70.0
    assert b2.speed == 70.0
    assert b3.speed == 100.0
