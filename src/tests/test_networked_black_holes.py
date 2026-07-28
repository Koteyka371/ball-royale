import pytest
from ai.game_modes import GAME_MODES, NetworkedBlackHolesMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.teleport_cooldown = 0.0

def test_networked_black_holes_spawns_black_holes():
    mode = GAME_MODES['networked_black_holes']
    world = MockWorld()
    balls = [MockBall(1, 500, 500)]

    mode.setup(world, balls)

    assert len(world.arena.hazards) >= 2
    for h in world.arena.hazards:
        if isinstance(h, dict):
            assert h["kind"] == "black_hole"
        else:
            assert getattr(h, "kind", "") == "black_hole"

def test_networked_black_holes_teleports():
    mode = GAME_MODES['networked_black_holes']
    world = MockWorld()
    ball = MockBall(1, 500, 500)
    balls = [ball]

    mode.setup(world, balls)

    # Activate network
    mode.timer = 11.0
    ball.teleport_cooldown = 0.0
    mode.tick(world, balls, 0.016)

    assert mode.network_active

    # Teleport ball
    bh1 = world.arena.hazards[0]
    if isinstance(bh1, dict):
        ball.x = bh1["x"] + 10.0
        ball.y = bh1["y"] + 10.0
    else:
        ball.x = getattr(bh1, "x") + 10.0
        ball.y = getattr(bh1, "y") + 10.0

    ball.teleport_cooldown = 0.0
    mode.tick(world, balls, 0.016)

    bh2 = world.arena.hazards[1]
    bh2_x = bh2["x"] if isinstance(bh2, dict) else getattr(bh2, "x")
    bh2_y = bh2["y"] if isinstance(bh2, dict) else getattr(bh2, "y")

    assert ball.x == bh2_x
    assert ball.y == bh2_y
    assert ball.teleport_cooldown == 2.0
