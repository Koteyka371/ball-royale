import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x, y, ball_type="basic"):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 50.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = ball_type
        self.speed_multiplier = 1.0
        self.perception_radius = 250.0
        self.solar_blinded = False

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, event_data):
        self.events.append((event_type, event_data))

def test_solar_radiation_storm_mode():
    mode = GAME_MODES["solar_radiation_storm"]
    world = MockWorld()

    # We will initialize hp to 50 so b3 can be buffed
    b1 = MockBall(1, 450, 450) # Open (dot = 200 * 0.707 * 2 = 282 > 200)
    b1.hp = 100.0 # b1 should be full health to start
    b2 = MockBall(2, 300, 300) # Shade (dot = 50 * 0.707 * 2 = 70.7)
    b2.hp = 100.0
    b3 = MockBall(3, 800, 800, ball_type="solar_bot") # Open

    balls = [b1, b2, b3]

    mode.setup(world, balls)

    mode.solar_walls = [
        type('Wall', (object,), {
            'x': 250,
            'y': 250,
            'width': 100,
            'height': 50,
            'angle': 0,
            'destructible': False,
            'hp': 999999,
            'max_hp': 999999,
            'is_solar_shield': True,
            'kind': 'indestructible_wall'
        })()
    ]
    world.arena.hazards = mode.solar_walls

    # Tick before flare
    mode.tick(world, balls, delta=19.9)
    assert not mode.is_flaring

    # Trigger flare
    mode.tick(world, balls, delta=0.2)
    assert mode.is_flaring

    # Run another tick
    mode.tick(world, balls, delta=1.0)

    assert b1.hp < 100.0
    assert b1.perception_radius == 50.0

    assert b2.hp == 100.0
    assert b2.perception_radius == 250.0

    assert b3.hp > 50.0
    assert b3.speed_multiplier >= 2.0

    # Pass flare duration
    mode.tick(world, balls, delta=5.0)
    assert not mode.is_flaring
    assert b1.perception_radius == 250.0

if __name__ == "__main__":
    test_solar_radiation_storm_mode()
    print("Success")
