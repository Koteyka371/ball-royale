
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x, y, hp):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = True
        self.ball_type = "player"

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        self.arena = MockArena()

def test_br_time_reversal_outside_zone():
    mode = GAME_MODES["battle_royale"]
    world = MockWorld()

    # Place a ball in the center initially
    ball = MockBall("test_time_trap", 500.0, 500.0, 100.0)
    balls = [ball]

    mode.setup(world, balls)
    mode.zone_radius = 500.0 # Force small zone for testing
    mode.zone_x = 500.0
    mode.zone_y = 500.0

    # Ensure path history is clear
    mode.player_path_history = {}

    # Tick 1: inside zone
    ball.x = 500.0
    ball.y = 500.0
    mode.tick(world, balls, delta=1.0)
    hist1_x, hist1_y = mode.player_path_history["test_time_trap"][-1]

    # Tick 2: slightly moving
    ball.x = 510.0
    ball.y = 510.0
    mode.tick(world, balls, delta=1.0)
    hist2_x, hist2_y = mode.player_path_history["test_time_trap"][-1]

    # Tick 3: slightly moving
    ball.x = 520.0
    ball.y = 520.0
    mode.tick(world, balls, delta=1.0)
    hist3_x, hist3_y = mode.player_path_history["test_time_trap"][-1]

    # Now step outside the zone
    ball.x = 9000.0
    ball.y = 9000.0

    # Tick 4: outside zone -> should revert to Tick 3
    mode.tick(world, balls, delta=1.0)
    assert ball.x == hist3_x
    assert ball.y == hist3_y

    # Set it far away again
    ball.x = 9000.0
    ball.y = 9000.0

    # Tick 5: outside zone -> should revert to Tick 2
    mode.tick(world, balls, delta=1.0)
    assert ball.x == hist2_x
    assert ball.y == hist2_y

    # Set it far away again
    ball.x = 9000.0
    ball.y = 9000.0

    # Tick 6: outside zone -> should revert to Tick 1
    mode.tick(world, balls, delta=1.0)
    assert ball.x == hist1_x
    assert ball.y == hist1_y

    # Set it far away again
    ball.x = 9000.0
    ball.y = 9000.0

    # Tick 7: outside zone, history empty -> should get pulled towards center slightly
    mode.tick(world, balls, delta=1.0)
    assert ball.x < 9000.0 # Pulled closer
    assert ball.y < 9000.0

    # Verify no damage taken
    assert ball.hp == 100.0
    assert ball.alive

if __name__ == "__main__":
    test_br_time_reversal_outside_zone()
    print("test_br_time_reversal_outside_zone passed")
