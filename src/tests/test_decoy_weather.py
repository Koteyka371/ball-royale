import math
from ai.action import Action
from ai.game_modes import ExtremeWeatherMode

class MockWorld:
    def __init__(self, balls=None):
        self.balls = balls if balls else []
        self.events = []
        self.tick = 0
        self.next_id = 1000
        self.arena = MockArena()
        self.game_mode = ExtremeWeatherMode()

class MockArena:
    def __init__(self):
        self.hazards = []

class MockBall:
    def __init__(self, id, x, y, team="A"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.alive = True
        self.is_decoy = False

def test_decoy_blizzard_weather():
    world = MockWorld()
    world.game_mode.current_weather = "blizzard"

    decoy = MockBall(1, 100, 100, "A")
    decoy.is_decoy = True
    decoy.decoy_timer = 0
    decoy.hp = 0
    decoy.alive = True

    enemy = MockBall(2, 110, 110, "B")

    world.balls = [decoy, enemy]

    action = Action(decoy, world)
    action.execute("idle", 0.1)

    # Check that decoy element was applied (freeze_timer on enemy)
    assert getattr(enemy, "freeze_timer", 0.0) > 0.0

    # Check that ice_patch was spawned
    hazards = world.arena.hazards
    assert any(getattr(h, "kind", "") == "ice_patch" for h in hazards)

def test_decoy_acid_rain_weather():
    world = MockWorld()
    world.game_mode.current_weather = "acid_rain"

    decoy = MockBall(1, 100, 100, "A")
    decoy.is_decoy = True
    decoy.decoy_timer = 0
    decoy.hp = 0

    world.balls = [decoy]

    action = Action(decoy, world)
    action.execute("idle", 0.1)

    hazards = world.arena.hazards
    assert any(getattr(h, "kind", "") == "neutralizing_puddle" for h in hazards)
