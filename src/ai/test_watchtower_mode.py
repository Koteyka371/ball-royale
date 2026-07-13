import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.speed = 100.0
        self.base_speed = 100.0
        self.vision_radius = 500.0
        self.projectile_speed = 300.0
        self.traits = []

def test_watchtower():
    mode = GAME_MODES.get('watchtower')
    assert mode is not None

    world = MockWorld()
    b = MockBall(500, 500)
    balls = [b]

    mode.setup(world, balls)

    # After GameMode.setup, speed is modified by season / weekly modifiers!
    # Let's save the actual modified speed for comparison
    expected_speed = b.speed
    expected_vision = b.vision_radius
    expected_proj_speed = b.projectile_speed

    mode.tower_spawn_timer = 0.0 # Force spawn

    mode.tick(world, balls, 0.016)

    assert len(mode.towers) == 1

    t = mode.towers[0]

    # Not on tower
    assert b.speed == expected_speed

    # Move to tower
    b.x = t["x"]
    b.y = t["y"]

    mode.tick(world, balls, 0.016)

    # On tower
    assert b.speed == 0.0
    assert b.vision_radius == expected_vision * 3.0
    assert b.projectile_speed == expected_proj_speed * 2.0

    # Move off tower
    b.x = t["x"] + 200
    b.y = t["y"] + 200

    mode.tick(world, balls, 0.016)

    # Restored
    assert b.speed == expected_speed
    assert b.vision_radius == expected_vision
    assert b.projectile_speed == expected_proj_speed

    print("Test passed!")

if __name__ == "__main__":
    test_watchtower()
