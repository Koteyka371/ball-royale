from ai.game_modes import PulsingGravityWellMode
import math

class DummyArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class DummyBall:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.alive = True
        self.ball_type = "normal"
        self.team = "Red"
        self.vx = 0.0
        self.vy = 0.0
        self.score = 0

def test_pulsing_gravity_well_score():
    mode = PulsingGravityWellMode()
    world = DummyWorld()

    # Ball inside the 200 radius zone (center is 500, 500)
    b1 = DummyBall(500.0, 500.0, 10.0)
    # Ball outside the zone
    b2 = DummyBall(900.0, 900.0, 10.0)

    balls = [b1, b2]
    mode.setup(world, balls)

    # Tick past 0.5 to trigger scoring
    mode.tick(world, balls, 0.6)

    assert b1.score == 1
    assert b2.score == 0

def test_pulsing_gravity_well_pulse():
    mode = PulsingGravityWellMode()
    world = DummyWorld()

    # Ball slightly off center
    b1 = DummyBall(500.0, 510.0, 10.0)
    balls = [b1]

    mode.setup(world, balls)

    # Tick past 10.0 to trigger pulse
    mode.tick(world, balls, 10.1)

    # Check if pulse event was emitted
    assert any(e[0] == "gravity_pulse" for e in world.events)

    # Check if ball got pushed away
    # Center is 500, 500. Ball is at 500, 510.
    # dx = 0, dy = 10. dist = 10
    # nx = 0, ny = 1.
    # push = 1500 - 10 = 1490
    # b1.vy should be 1490
    assert b1.vy == 1490.0
    assert b1.vx == 0.0

def test_pulsing_gravity_well_winner():
    mode = PulsingGravityWellMode()
    world = DummyWorld()

    b1 = DummyBall(500.0, 500.0, 10.0)
    b1.team = "Blue"
    balls = [b1]

    mode.setup(world, balls)

    # Not enough points
    b1.score = 99
    assert mode.check_winner(world, balls) is None

    # Winner
    b1.score = 100
    assert mode.check_winner(world, balls) == "Blue"
