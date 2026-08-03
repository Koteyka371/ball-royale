import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.underground = False
        self.is_invisible = False
        self.tunnel_cooldown = 0.0
        self.tunnel_target_x = 0.0
        self.tunnel_target_y = 0.0
        self.speed_boost_timer = 0.0
        self.team = "A"

def test_tunnel_speed_boost_and_trail():
    mode = GAME_MODES.get("underground_tunnels")
    world = MockWorld()
    b1 = MockBall(1, 100.0, 100.0)
    balls = [b1]

    mode.setup(world, balls)
    t = mode.tunnels[0]

    b1.x = t.x1 + 10.0
    b1.y = t.y1 + 10.0

    # Tick to enter tunnel
    mode.tick(world, balls, delta=0.1)

    # verify teleport and trail
    assert b1.x == t.x2
    assert b1.y == t.y2
    assert b1.speed_boost_timer > 0.0
    assert b1.speed_boost_multiplier == 1.5

    # verify trail hazard created
    trails = [h for h in world.arena.hazards if getattr(h, "kind", "") == "deployable_thin_hazard_line"]
    assert len(trails) > 0
    trail = trails[-1]
    assert trail.start_x == t.x1
    assert trail.start_y == t.y1
    assert trail.end_x == t.x2
    assert trail.end_y == t.y2
    assert trail.team == "A"
