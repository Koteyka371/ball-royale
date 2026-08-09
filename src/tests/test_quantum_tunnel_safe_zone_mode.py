import sys
sys.path.append("src")
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.dead_balls = []

    def add_event(self, t, data):
        self.events.append({"type": t, "data": data})

class MockBall:
    def __init__(self, x=0.0, y=0.0):
        self.id = 1
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "player"
        self.hp = 100.0
        self.slow_timer = 0.0

def test_quantum_tunnel_safe_zone_mode():
    mode = GAME_MODES.get("quantum_tunnel_safe_zone")
    assert mode is not None

    world = MockWorld()

    # Ball 1 inside a biome (e.g. 250, 250)
    b1 = MockBall(250.0, 250.0)
    b1.id = 1

    # Ball 2 outside all biomes (e.g. 500, 500)
    b2 = MockBall(500.0, 500.0)
    b2.id = 2

    balls = [b1, b2]

    mode.setup(world, balls)

    # Tick without teleport trigger
    mode.tick(world, balls, 0.1)

    # Ball 2 should take damage
    assert b2.hp < 100.0
    # Ball 2 should be slowed
    assert b2.slow_timer > 0.0

    # Ball 1 should take no damage
    assert b1.hp == 100.0

    # Fast forward teleport timer
    mode.teleport_timer = 7.95
    old_b1_x = b1.x
    old_b1_y = b1.y

    mode.tick(world, balls, 0.1)

    # Ball 1 should be teleported to a DIFFERENT biome
    # Current biome index for Ball 1 was 0 (250, 250)
    # The other biomes are at (750, 250), (250, 750), (750, 750)
    # After teleportation, Ball 1's position should NOT be near 250, 250
    dist_from_old = math.hypot(b1.x - old_b1_x, b1.y - old_b1_y)
    assert dist_from_old > 200.0, "Ball 1 should have teleported far away"

    # Verify event was emitted
    teleport_events = [e for e in world.events if e["type"] == "quantum_teleport"]
    assert len(teleport_events) > 0
