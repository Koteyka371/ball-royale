import sys
import math
sys.path.append("src")
from ai.game_modes import GAME_MODES

def test_solar_radiation_storm():
    mode = GAME_MODES["solar_radiation_storm"]

    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()
            self.events = []

        def add_event(self, type, data=None):
            self.events.append((type, data))

    class MockBall:
        def __init__(self, x, y, ball_type="normal"):
            self.x = x
            self.y = y
            self.ball_type = ball_type
            self.alive = True
            self.hp = 100.0
            self.max_hp = 120.0
            self.perception_radius = 250.0
            self.speed_multiplier = 1.0
            self.base_perception_radius = 250.0
            self.solar_blinded = False

    world = MockWorld()
    b1 = MockBall(500, 500, "solar_bot") # Should buff
    b2 = MockBall(500, 500, "normal") # Should damage

    mode.setup(world, [b1, b2])
    # Keep only one wall to prevent random shade on b1
    mode.solar_walls = [mode.solar_walls[0]]

    # Start flaring
    mode.flare_timer = 21.0
    mode.tick(world, [b1, b2], delta=0.016) # Triggers flare start

    # Now it is flaring
    wall = mode.solar_walls[0]
    wall.x = 550
    wall.y = 550
    wall.width = 200
    wall.height = 50

    b3 = MockBall(600, 600, "normal") # Shade

    mode.tick(world, [b1, b2, b3], delta=1.0) # Apply damage/buff

    assert b1.hp == 120.0
    assert b2.hp < 100.0
    assert b3.hp == 100.0
    assert b2.solar_blinded == True
    assert b2.perception_radius == 50.0

    # tick until end
    mode.flare_timer = 6.0
    mode.tick(world, [b1, b2, b3], delta=1.0)
    assert not mode.is_flaring
    assert not b2.solar_blinded
    assert b2.perception_radius == 250.0

test_solar_radiation_storm()
print("All assertions passed")
