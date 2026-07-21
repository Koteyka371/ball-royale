from ai.game_modes import WhirlpoolsMode

class MockArena:
    def __init__(self):
        self.width = 800
        self.height = 800
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.hp = 100.0

def test_whirlpools_mode():
    mode = WhirlpoolsMode()
    world = MockWorld()

    b_far = MockBall(10, 10)
    b_center = MockBall(405, 405)

    mode.setup(world, [b_far, b_center])

    assert len(world.arena.hazards) == 2
    for h in world.arena.hazards:
        assert getattr(h, "kind") == "whirlpool"

    w = world.arena.hazards[0]
    w.x = 400
    w.y = 400

    delta = 0.016
    mode.tick(world, [b_far, b_center], delta)

    assert b_far.vx == 0.0
    assert b_far.vy == 0.0
    assert not hasattr(b_far, "submerge_timer")

    assert hasattr(b_center, "submerge_timer")
    assert b_center.submerge_timer == 1.5
    assert hasattr(b_center, "wet_timer")
    assert b_center.wet_timer == 3.0
    assert b_center.hp < 100.0

    b_edge = MockBall(600, 400)
    mode.tick(world, [b_edge], delta)

    assert b_edge.vx < 0.0
