from ai.game_modes import GAME_MODES, ReverseBlackHoleMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, kind, payload):
        self.events.append((kind, payload))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "normal"
        self.vx = 0.0
        self.vy = 0.0
        self.weather_immunity_timer = 0.0

def test_reverse_black_hole_mode_exists():
    assert 'reverse_black_hole_event' in GAME_MODES
    assert isinstance(GAME_MODES['reverse_black_hole_event'], ReverseBlackHoleMode)

def test_reverse_black_hole_push():
    world = MockWorld()
    b = MockBall(500, 500)
    mode = ReverseBlackHoleMode()

    # Force active
    mode.active = True
    mode.timer = 10.0
    mode.zone_x = 500
    mode.zone_y = 500
    mode.radius = 200

    # Place ball at 510, 500
    b.x = 510

    mode.tick(world, [b], delta=1.0)

    assert b.vx > 0.0, "Ball should be pushed to the right"
    assert b.x == 510, "Ball should not have its position mutated if vx/vy exist"
