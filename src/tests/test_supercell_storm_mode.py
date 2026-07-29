import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, team, x, y):
        self.id = f"ball_{team}"
        self.team = team
        self.ball_type = team
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100.0

    def take_damage(self, amount):
        self.hp -= amount

def test_supercell_storm_mode():
    mode = GAME_MODES["supercell_storm"]
    world = MockWorld()

    # Two balls: one in outer vortex, one very far
    b1 = MockBall("red", 500.0, 550.0)
    b2 = MockBall("blue", 900.0, 900.0)
    balls = [b1, b2]

    mode.setup(world, balls)

    assert world.arena.weather == "thunderstorm"
    assert world.arena.is_night == True

    # Tick to spawn the supercell_tornado
    # Wind timer starts at 20.0
    mode.wind_timer = 0.1
    mode.tick(world, balls, 0.2)

    assert len(world.arena.hazards) == 1
    tornado = world.arena.hazards[0]
    assert tornado.kind == "supercell_tornado"
    assert tornado.radius == 100.0

    # Force tornado position near b1
    tornado.x = 500.0
    tornado.y = 500.0

    # Tick to trigger lightning
    mode.lightning_timer = 0.1
    mode.tick(world, balls, 0.2)

    # Check if b1 was struck by chain lightning (in outer vortex, dist_sq = 2500, inner radius = 30.0 -> 900, outer = 10000)
    # So 900 < 2500 <= 10000 -> True
    assert b1.hp < 100.0

    # Check events
    assert any(e[0] == "chain_lightning_strike" and e[1]["target"] == "ball_red" for e in world.events)
