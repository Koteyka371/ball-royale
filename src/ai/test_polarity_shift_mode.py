from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "normal"

class MockHazard:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kind = "spikes"

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_polarity_shift_mode_state_a():
    mode = GAME_MODES["polarity_shift"]
    world = MockWorld()
    # Center is 500, 500
    b = MockBall(600, 500) # dx=100, dy=0
    h = MockHazard(400, 500) # dx=-100, dy=0
    world.arena.hazards.append(h)

    mode.setup(world, [b])

    assert mode.polarity_state == 1

    mode.tick(world, [b], 1.0)

    # State 1: push balls out -> b moves right (+150 * 1.0) -> x=750
    # State 1: pull hazards in -> h moves right (+150 * 1.0) -> x=550

    assert b.x > 600
    assert h.x > 400

def test_polarity_shift_mode_state_b():
    mode = GAME_MODES["polarity_shift"]
    world = MockWorld()
    # Center is 500, 500
    b = MockBall(600, 500) # dx=100, dy=0
    h = MockHazard(400, 500) # dx=-100, dy=0
    world.arena.hazards.append(h)

    mode.setup(world, [b])

    # Trigger state flip
    mode.tick(world, [b], 11.0)

    assert mode.polarity_state == -1

    # Check event
    assert len(world.events) > 0
    assert world.events[0][0] == "polarity_shift"

    # Check movement
    # Before move logic runs, timer resets, state goes to -1.
    # State -1: pull balls in -> b moves left (-150 * 11.0)
    # State -1: push hazards out -> h moves left (-150 * 11.0)

    assert b.x < 600
    assert h.x < 400
