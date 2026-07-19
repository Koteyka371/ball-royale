import sys
sys.path.append("src")
from ai.game_modes import ExtremeWeatherMode

class MockWorld:
    def __init__(self):
        self.boosters = []
        self.arena = type("Arena", (), {"width": 1000, "height": 1000})()

mode = ExtremeWeatherMode()
world = MockWorld()
mode.setup(world, [])

# Trigger weather changes to see if they spawn boosters
for _ in range(200):
    mode.tick(world, [], 0.1)

print(f"Weather: {mode.current_weather}, Boosters: {[b.kind for b in world.boosters]}")
