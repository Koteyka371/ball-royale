from ai.game_modes import EndGameMagnetMode, GAME_MODES

def test_end_game_magnet_no_activate_early():
    mode = GAME_MODES['end_game_magnet']
    mode.total_match_time = 30.0

    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
            self.boosters = []

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()
            self.boosters = []

    world = MockWorld()
    balls = []
    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 0

def test_end_game_magnet_activate():
    mode = GAME_MODES['end_game_magnet']
    mode.total_match_time = 70.0

    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
            self.boosters = []

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()
            self.boosters = []

    world = MockWorld()

    class MockBall:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.vx = 0.0
            self.vy = 0.0
            self.alive = True
            self.ball_type = "normal"

    class MockBooster:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.vx = 0.0
            self.vy = 0.0
            self.kind = "booster"

    class MockHazard:
        def __init__(self, x, y, radius):
            self.x = x
            self.y = y
            self.vx = 0.0
            self.vy = 0.0
            self.radius = radius
            self.kind = "small_hazard"
            self.id = 12345

    b1 = MockBall(100, 500)
    balls = [b1]

    booster = MockBooster(900, 500)
    world.boosters.append(booster)

    hazard = MockHazard(500, 100, 20.0)
    world.arena.hazards.append(hazard)

    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 2
    magnet = next((h for h in world.arena.hazards if getattr(h, "kind", "") == "end_game_magnet"), None)
    assert magnet is not None
    assert magnet.x == 500
    assert magnet.y == 500

    # Magnet is at (500, 500).
    # Ball is at (100, 500) -> should be pulled right (vx > 0)
    assert b1.vx > 0

    # Booster is at (900, 500) -> should be pulled left (vx < 0)
    assert booster.vx < 0

    # Hazard is at (500, 100) -> should be pulled down (vy > 0)
    assert hazard.vy > 0
