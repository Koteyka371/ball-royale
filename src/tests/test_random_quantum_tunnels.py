import sys
sys.path.append("src")
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 2000.0
        self.height = 2000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, t, data):
        self.events.append({"type": t, "data": data})

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 100.0
        self.y = 100.0
        self.vx = 50.0
        self.vy = 50.0
        self.alive = True
        self.ball_type = "player"
        self.team = 1

def test_random_quantum_tunnels():
    mode = GAME_MODES.get("random_quantum_tunnels")
    assert mode is not None

    world = MockWorld()
    ball = MockBall()

    mode.setup(world, [ball])
    assert len(mode.tunnels) == 3

    # Place ball directly on a tunnel
    t = mode.tunnels[0]
    ball.x = t.x
    ball.y = t.y

    mode.tick(world, [ball], 0.1)

    # Verify teleport and velocity inversion
    assert ball.x == 2000.0 - t.x
    assert ball.y == 2000.0 - t.y
    assert ball.vx == -50.0
    assert ball.vy == -50.0
    assert hasattr(ball, "quantum_tunnel_cooldown") and getattr(ball, "quantum_tunnel_cooldown") > 0.0
