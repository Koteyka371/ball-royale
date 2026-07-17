from ai.game_modes import GameMode, GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y, radius):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.alive = True
        self.ball_type = "player"

class MockHazard:
    def __init__(self, id, x, y, radius, kind, damage=10.0):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage

def test_quantum_shift_hazards():
    assert "quantum_shift_hazards" in GAME_MODES
    mode = GAME_MODES["quantum_shift_hazards"]

    world = MockWorld()
    h = MockHazard(1, 100, 100, 20, "puddle", 5.0)
    world.arena.hazards.append(h)

    b = MockBall(1, 100, 100, 10)

    # We monkeypatch random to always trigger
    import random
    orig_random = random.random
    random.random = lambda: 0.1

    try:
        mode.setup(world, [b])
        mode.tick(world, [b], 0.1)

        assert h.kind == "quantum_teleporter"
        assert h.damage == 0.0

        # move the ball away so it doesn't re-trigger it instantly
        b.x = 999
        b.y = 999

        mode.tick(world, [b], 5.0)

        assert h.kind == "puddle"
        assert h.damage == 5.0
    finally:
        random.random = orig_random
