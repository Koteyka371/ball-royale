class MockBall:
    def __init__(self, id, x, y, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.alive = alive
        self.hp = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.ball_type = "basic"
        self.radius = 10.0

class MockHazard:
    def __init__(self, id, x, y, radius, kind, duration=10.0, lifetime=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.duration = duration
        self.lifetime = lifetime

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000.0
        self.height = 1000.0
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.events = []
        self.tick = 1
        self.next_id = 9999

def test_black_hole_merge():
    from ai.action import Action
    world = MockWorld()
    b1 = MockBall(1, 500, 500)
    world.balls.append(b1)

    bh1 = MockHazard(1, 100, 100, 100, "black_hole")
    bh2 = MockHazard(2, 100, 110, 80, "black_hole")
    world.arena.hazards.extend([bh1, bh2])

    action = Action(b1, world)
    action.execute('idle', 1.0)

    # Check merge
    assert bh1.radius == 140.0
    assert bh2.duration == 0.0

def test_black_hole_supernova():
    from ai.action import Action
    world = MockWorld()
    b1 = MockBall(1, 500, 500)
    b2 = MockBall(2, 900, 900)
    world.balls.extend([b1, b2])

    bh1 = MockHazard(1, 100, 100, 150, "massive_black_hole")
    world.arena.hazards.append(bh1)

    action = Action(b1, world)
    action.execute('idle', 1.0)

    # Both should be dead due to supernova blast
    assert b1.hp <= 0
    assert b1.alive == False
    assert b1.killer == "supernova_explosion"
    assert b2.hp <= 0
    assert b2.alive == False
    assert b2.killer == "supernova_explosion"
    assert bh1.duration == 0.0
