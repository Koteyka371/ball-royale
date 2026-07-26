import sys
sys.path.append("src")
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, team, x, y):
        self.team = team
        self.ball_type = "test_ball"
        self.alive = True
        self.x = x
        self.y = y
        self.radius = 20.0
        self.score = 0.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, kind, data):
        self.events.append((kind, data))

def test_dynamic_capture_zones():
    mode = GAME_MODES["dynamic_capture_zones"]
    world = MockWorld()

    # Initialize the zone directly for testing
    mode.zone = {
        "x": 500.0,
        "y": 500.0,
        "vx": 0.0,
        "vy": 0.0,
        "radius": 300.0,
        "min_radius": 50.0,
        "shrink_rate": 2.0
    }

    # One team inside the zone
    b1 = MockBall("Red", 500, 500)
    balls = [b1]

    mode.apply_dynamic_traits(world, balls, 1.0)
    assert b1.score == 10.0
    assert mode.zone["radius"] == 298.0

    # Multiple teams inside the zone
    b2 = MockBall("Blue", 510, 500)
    balls.append(b2)

    mode.apply_dynamic_traits(world, balls, 1.0)
    # Score should not increase because contested
    assert b1.score == 10.0
    assert b2.score == 0.0
    assert mode.zone["radius"] == 296.0

    print("test_dynamic_capture_zones passed")

if __name__ == "__main__":
    test_dynamic_capture_zones()
