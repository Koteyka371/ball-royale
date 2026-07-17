from ai.game_modes import HauntedArenaEventMode

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, event_data):
        self.events.append((event_type, event_data))

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.is_night = False
        self.is_haunted = False
        self.hazards = []

def test_haunted_arena_event():
    mode = HauntedArenaEventMode()
    world = MockWorld()
    balls = []

    # Fast forward to trigger
    mode.event_timer = 31.0
    mode.random.random = lambda: 0.1 # trigger

    mode.tick(world, balls, 0.1)

    assert mode.event_active is True
    assert world.arena.is_haunted is True
    assert world.arena.is_night is True
    assert len(world.events) == 2

    # Fast forward to spawn hazard
    mode.spawn_timer = 6.0
    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "spectral_clone"

    class MovingBall:
        def __init__(self, id_val, x, y, vx, vy):
            self.id = id_val
            self.x = x
            self.y = y
            self.vx = vx
            self.vy = vy
            self.alive = True
        def get(self, prop, default=None):
            return getattr(self, prop, default)

    moving_ball = MovingBall(1, 500, 500, 100, 0)
    world.balls = [moving_ball]

    # Tick many times to get trails reliably
    initial_event_count = len(world.events)
    for _ in range(50):
        mode.tick(world, world.balls, 0.1)

    has_trail = False
    for event_type, event_data in world.events:
        if event_type == "footstep_trail":
            has_trail = True
            break
    assert has_trail

    # Fast forward to end
    mode.event_duration = 0.0
    mode.tick(world, balls, 0.1)

    assert mode.event_active is False
    assert world.arena.is_haunted is False
    assert world.arena.is_night is False
    assert len(world.arena.hazards) == 0
