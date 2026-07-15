import math
from src.ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        class LBM:
            data = {"weekly_mutator": "none", "seasonal_mutator": "none"}
            def get(self, k, default=0): return 0
        self.leaderboard_manager = LBM()

class MockBall:
    def __init__(self, id):
        self.id = id
        self.x = 200.0
        self.y = 200.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.base_speed = 300.0
        self.speed = 300.0
        self.alive = True
        self.ball_type = "player"
        self.silenced = False

def test_elastic_band_zone():
    mode = GAME_MODES.get("elastic_band_zone")
    assert mode is not None

    world = MockWorld()
    b1 = MockBall("b1")
    mode.setup(world, [b1])

    assert mode.zone_x == 500.0
    assert mode.zone_y == 500.0

    # Not in zone
    mode.tick(world, [b1], 0.1)
    assert b1.id not in mode.grabbed_state

    # Enter zone with velocity
    b1.x = 450.0
    b1.y = 450.0
    b1.velocity_x = 200.0
    b1.velocity_y = 0.0
    b1.base_speed = 300.0
    b1.speed = 300.0

    # In tick, super.setup might mutate base_speed

    # Just save whatever it becomes after tick 1

    mode.tick(world, [b1], 0.1)

    assert b1.id in mode.grabbed_state
    orig_speed = mode.grabbed_state[b1.id]["original_speed"]

    assert b1.speed == 0.0
    assert b1.base_speed == 0.0
    assert b1.velocity_x == 0.0
    assert b1.silenced == True

    # Tick until launch
    for _ in range(10):
        mode.tick(world, [b1], 0.1)

    assert b1.id not in mode.grabbed_state
    assert getattr(b1, "elastic_cooldown", 0) > 0
    assert b1.speed == orig_speed * 3.0
    assert b1.base_speed == orig_speed * 3.0
    assert b1.velocity_x == -orig_speed * 3.0 # entered from left moving right, should bounce back left
    assert b1.velocity_y == 0.0
    assert b1.silenced == False

if __name__ == "__main__":
    test_elastic_band_zone()
    print("Test passed!")
