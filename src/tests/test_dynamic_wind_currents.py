import sys
import os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, ball_id, ball_type="warrior", alive=True):
        self.id = ball_id
        self.ball_type = ball_type
        self.alive = alive
        self.vx = 0.0
        self.vy = 0.0

class MockHazard:
    def __init__(self, kind="projectile"):
        self.kind = kind
        self.vx = 0.0
        self.vy = 0.0

def test_dynamic_wind_currents_mode():
    mode = GAME_MODES["dynamic_wind_currents"]
    world = MockWorld()

    # Initialize some balls
    ball1 = MockBall(1)
    ball2 = MockBall(2, "spectator")
    dead_ball = MockBall(3, alive=False)
    balls = [ball1, ball2, dead_ball]

    # Initialize a projectile hazard
    projectile = MockHazard("projectile")
    non_projectile = MockHazard("rock")
    world.arena.hazards.extend([projectile, non_projectile])

    # Force the timer to 0 so wind shifts
    mode.wind_change_timer = 0.0

    # Tick with delta 0.1
    mode.apply_dynamic_traits(world, balls, 0.1)

    # Assert wind direction and strength are set
    assert mode.wind_strength > 0
    assert mode.wind_dir_x != 0.0 or mode.wind_dir_y != 0.0

    # Assert event was triggered
    assert len(world.events) > 0
    assert world.events[0][0] == "wind_shift"

    # Check ball vx and vy
    # Ball 1 (alive) should have new vx and vy
    assert ball1.vx != 0.0 or ball1.vy != 0.0
    assert ball1.vx == mode.wind_dir_x * mode.wind_strength * 0.1

    # Ball 2 (spectator) should not be moved
    assert ball2.vx == 0.0 and ball2.vy == 0.0

    # Dead ball should not be moved
    assert dead_ball.vx == 0.0 and dead_ball.vy == 0.0

    # Check projectile hazard
    assert projectile.vx != 0.0 or projectile.vy != 0.0
    assert projectile.vx == mode.wind_dir_x * mode.wind_strength * 0.1

    # Check non-projectile hazard
    assert non_projectile.vx == 0.0 and non_projectile.vy == 0.0

if __name__ == "__main__":
    test_dynamic_wind_currents_mode()
    print("Test passed.")
