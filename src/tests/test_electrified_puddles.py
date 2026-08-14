from ai.game_modes import GameMode
from arena.procedural_arena import Hazard

class MockArena:
    def __init__(self):
        self.hazards = []
        self.weather = "thunderstorm"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

class MockBall:
    def __init__(self, x, y, b_type="normal"):
        self.x = x
        self.y = y
        self.radius = 15.0
        self.alive = True
        self.ball_type = b_type
        self.traits = []
        self.speed = 100.0
        self.hp = 100.0

def test_puddle_slow_and_electrify():
    world = MockWorld()
    world.arena.weather = "thunderstorm"
    puddle = Hazard(id=1, x=100.0, y=100.0, radius=50.0, kind="puddle", damage=0.0)
    world.arena.hazards.append(puddle)

    mode = GameMode()
    mode.random = __import__("random")

    b1 = MockBall(100.0, 100.0)
    b2 = MockBall(100.0, 100.0, "electric")
    b2.using_electric_skill = True

    # Tick without electric ball to test slow
    mode.apply_dynamic_traits(world, [b1], 1.0)
    assert b1.speed == 70.0
    assert not getattr(puddle, "electrified", False)

    # Tick with electric ball to electrify
    mode.apply_dynamic_traits(world, [b1, b2], 1.0)
    assert getattr(puddle, "electrified", False)

    # Tick again to test damage on b1
    b1.hp = 100.0
    mode.apply_dynamic_traits(world, [b1, b2], 1.0)
    assert b1.hp < 100.0
    assert b2.hp == 100.0
