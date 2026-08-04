import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.game_modes import TugOfWarMultiplePayloadsMode

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        class Arena:
            width = 1000.0
            height = 1000.0
        self.arena = Arena()

class MockBall:
    def __init__(self, x=500.0, y=500.0, team="Neutral", ball_type="player", alive=True, radius=10.0):
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.alive = alive
        self.radius = radius
        self.vx = 0.0
        self.vy = 0.0

def test_tug_of_war_multiple_payloads():
    mode = TugOfWarMultiplePayloadsMode()
    world = MockWorld()

    b1 = MockBall(team="Red")
    b2 = MockBall(team="Blue")
    balls = [b1, b2]

    mode.setup(world, balls)

    # Check that 3 payloads were spawned
    assert len(mode.payloads) == 3
    for p in mode.payloads:
        assert getattr(p, "is_payload", False)
        assert p.ball_type == "payload"
        assert p.team == "Neutral"

    # Tick simulation
    mode.tick(world, balls, 0.016)

    # Check win conditions
    # Red pushed all to blue side
    for p in mode.payloads:
        p.x = 950.0

    winner = mode.check_winner(world, balls)
    assert winner == "Red"

    # Blue pushed all to red side
    for p in mode.payloads:
        p.x = 50.0

    winner = mode.check_winner(world, balls)
    assert winner == "Blue"
