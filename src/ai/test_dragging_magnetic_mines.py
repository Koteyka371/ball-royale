import pytest
from ai.game_modes import DraggingMagneticMinesMode

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

def test_dragging_magnetic_mines():
    mode = DraggingMagneticMinesMode()
    world = MockWorld()

    ball = MockBall(500, 500)
    mode.setup(world, [ball])

    # Place a single mine near the ball
    mode.mines = [{
        'x': 400,
        'y': 500,
        'activation_radius': 150,
        'state': 'inactive',
        'timer': 1.0,
        'pull_strength': 100,
        'explosion_damage': 50,
        'explosion_radius': 200
    }]
    mine = mode.mines[0]

    # First tick: should change state to dragging because ball is at dist 100 <= 150
    mode.tick(world, [ball], 0.1)
    assert mine['state'] == 'dragging'

    # Second tick: should drag ball
    # ball is at (500, 500). mine is at (400, 500). dx = 100, dy = 0
    # ball.x -= (100 / 100) * 100 * 0.1 = 10
    mode.tick(world, [ball], 0.1)
    assert ball.x == 490
    assert mine['timer'] == 0.9

    # Tick enough to explode
    mode.tick(world, [ball], 0.9)
    assert mine['state'] == 'exploded'

    # Explode should apply shockwave, not direct damage
    assert getattr(ball, 'vx', 0.0) != 0.0 or getattr(ball, 'vy', 0.0) != 0.0
    assert len(world.events) == 1
    assert world.events[0][0] == "massive_shockwave"
    assert world.events[0][1]["radius"] == 200
