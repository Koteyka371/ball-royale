import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x, y, vx=0.0, vy=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.hp = 100
        self.radius = 15.0
        self.is_confused = False
        self.confused_timer = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.game_mode = None

def test_dormant_decoys_mode():
    mode = GAME_MODES['dormant_decoys']
    world = MockWorld()
    balls = []

    # Setup mode
    mode.setup(world, balls)

    # Check decoys initialized
    assert len(mode.decoys) == 15
    assert all(not d['active'] for d in mode.decoys)

    # Force a decoy near a fast moving ball
    decoy = mode.decoys[0]
    decoy['x'] = 500
    decoy['y'] = 500

    fast_ball = MockBall(600, 500, vx=50.0, vy=0.0) # Within 200 units, fast speed > 30.0
    balls.append(fast_ball)

    mode.tick(world, balls, delta=0.1)

    # Decoy should be active
    assert decoy['active'] == True

    # Move ball very close to detonate
    fast_ball.x = 520

    mode.tick(world, balls, delta=0.1)

    # Decoy should be removed and exploded
    assert decoy not in mode.decoys
    assert len(world.arena.hazards) > 0
    assert fast_ball.hp < 100
    assert fast_ball.is_confused == True
