from ai.game_modes import GAME_MODES, GravityReversalMutatorMode, BlackHoleMode

class MockWorld:
    def __init__(self):
        self.arena = type("Arena", (), {"width": 1000, "height": 1000, "hazards": []})
        self.events = []
        self.is_gravity_reversed = False
        self.dead_balls = []

    def add_event(self, kind, data):
        self.events.append((kind, data))

def test_gravity_reversal_mutator_toggles_state():
    world = MockWorld()
    mode = GravityReversalMutatorMode()
    assert mode.is_gravity_reversed == False
    assert world.is_gravity_reversed == False
    mode.tick(world, [], delta=10.1)
    assert mode.is_gravity_reversed == True
    assert world.is_gravity_reversed == True
    mode.tick(world, [], delta=10.1)
    assert mode.is_gravity_reversed == False
    assert world.is_gravity_reversed == False

def test_blackhole_repels_when_reversed():
    world = MockWorld()
    world.is_gravity_reversed = True
    bh_mode = BlackHoleMode()
    bh_mode.black_hole_radius = 50.0
    class MockBall:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.alive = True
            self.ball_type = "player"
            self.weather_immunity_timer = 0.0
    b = MockBall(500, 400)
    balls = [b]
    import math
    initial_dist = math.hypot(500 - b.x, 500 - b.y)
    bh_mode.tick(world, balls, delta=0.1)
    new_dist = math.hypot(500 - b.x, 500 - b.y)
    assert new_dist > initial_dist
