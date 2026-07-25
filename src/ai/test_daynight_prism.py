from ai.game_modes import DayNightMode

class MockArena:
    def __init__(self):
        self.is_night = False
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, hp=100.0):
        self.alive = True
        self.ball_type = "normal"
        self.hp = hp
        self.x = 0.0
        self.y = 0.0
        self.radius = 15.0
        self.inventory = []

def test_sunlight_prism():
    mode = DayNightMode()
    world = MockWorld()
    mode.setup(world, [])

    # create sunlight beam overlapping with the prism
    mode.active_sunlight_beams.append({'x': 0.0, 'y': 0.0, 'radius': 100.0, 'duration': 10.0})

    # create a sunlight prism hazard
    prism = type("MockHazard", (), {"kind": "deployable_sunlight_prism", "x": 0.0, "y": 0.0, "radius": 20.0})()
    world.arena.hazards.append(prism)

    # Tick to see what happens to the beam or what the prism does.
    mode.tick(world, [], 0.1)

    # original beam should have its duration set to 0.0 and two new beams should be created
    assert len(mode.active_sunlight_beams) == 3
    assert mode.active_sunlight_beams[0]['duration'] == 0.0
    assert mode.active_sunlight_beams[1]['duration'] > 0.0
    assert mode.active_sunlight_beams[2]['duration'] > 0.0

    print("Test passed!")
