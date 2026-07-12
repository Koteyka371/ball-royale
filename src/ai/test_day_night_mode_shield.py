import sys
import os

sys.path.insert(0, os.path.abspath('src'))
from ai.game_modes import DayNightMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.is_night = False
        self.items = []
        self.hazards = []

class MockWorld2:
    def __init__(self):
        self.arena = MockArena()
        self.time_scale = 1.0
        self.events = []
    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100.0
        self.inventory = []
        self.ball_type = "normal"
        self.supercharge_timer = 0.0

def test_reflective_shield():
    mode = DayNightMode()
    world = MockWorld2()

    b1 = MockBall(x=500.0, y=500.0)
    b1.inventory = ["reflective_shield"]

    mode.setup(world, [b1])

    mode.active_sunlight_beams = []
    mode.active_sunlight_beams.append({'x': 500.0, 'y': 500.0, 'radius': 150.0, 'duration': 2.0})

    mode.tick(world, [b1], delta=0.1)

    assert "reflective_shield" not in b1.inventory, "Shield should be consumed"
    assert b1.hp == 100.0, f"Ball should take no damage, but hp is {b1.hp}"

    # We should have one more beam redirected
    assert len(mode.active_sunlight_beams) == 2, f"There should be 2 active beams now (1 original, 1 redirected), got {len(mode.active_sunlight_beams)}"
    redirected_beam = mode.active_sunlight_beams[-1]
    assert redirected_beam['radius'] == 75.0, "Redirected beam should be smaller"

    print("Python reflective shield test passed!")

if __name__ == '__main__':
    test_reflective_shield()
