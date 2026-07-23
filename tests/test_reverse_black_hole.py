import pytest
from ai.game_modes import GAME_MODES, GameMode

class DummyArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.events = []
    def add_event(self, kind, data):
        self.events.append((kind, data))

class DummyBall:
    def __init__(self, x, y):
        self.id = id(self)
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.ball_type = "basic"

def test_reverse_bh_mutator():
    mode = GAME_MODES.get("reverse_black_hole_mutator")
    world = DummyWorld()
    b1 = DummyBall(500, 500)
    balls = [b1]

    mode.setup(world, balls)

    # Fast forward time to spawn hazard
    mode.spawn_timer = 9.9
    mode.tick(world, balls, 0.2)

    hazards = world.arena.hazards
    assert len(hazards) == 1
    h = hazards[0]
    assert h.kind == "reverse_black_hole"

    # Place ball close to hazard
    b1.x = h.x + 10
    b1.y = h.y
    b1.vx = 0
    b1.vy = 0

    # Tick again
    mode.tick(world, balls, 0.1)

    assert b1.vx > 0 # Should be pushed away from center to the right
    assert b1.vy == 0
