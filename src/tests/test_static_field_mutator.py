import pytest
from ai.game_modes import GAME_MODES, StaticFieldMutatorMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

class MockBall:
    def __init__(self, ball_id, x, y, alive=True, ball_type="normal", traits=None, electric_immunity=False):
        self.id = ball_id
        self.x = x
        self.y = y
        self.alive = alive
        self.hp = 100.0
        self.speed_debuff_timer = 0.0
        self.speed_debuff_multiplier = 1.0
        self.ball_type = ball_type
        self.traits = traits or []
        self.electric_immunity = electric_immunity

def test_static_field_creation_from_event():
    mode = GAME_MODES.get("static_field_mutator")
    assert isinstance(mode, StaticFieldMutatorMode)

    world = MockWorld()
    balls = [MockBall(1, 100, 100)]

    # Emit a chain_lightning event with x, y
    world.events.append(("chain_lightning", {"x": 100, "y": 100}))

    mode.tick(world, balls, delta=0.016)

    assert len(world.arena.hazards) == 1
    h = world.arena.hazards[0]
    assert h["kind"] == "static_field"
    assert h["x"] == 100
    assert h["y"] == 100
    assert h["radius"] == 150.0
    assert h["duration"] > 0

def test_static_field_effects():
    mode = GAME_MODES.get("static_field_mutator")

    world = MockWorld()
    world.arena.hazards = [
        {"kind": "static_field", "x": 0, "y": 0, "radius": 150.0, "duration": 5.0}
    ]

    # Ball inside range, not immune
    b1 = MockBall(1, 50, 50, electric_immunity=False)
    # Ball inside range, immune via flag
    b2 = MockBall(2, -50, -50, electric_immunity=True)
    # Ball inside range, immune via type
    b3 = MockBall(3, 0, 50, ball_type="lightning_rod")
    # Ball inside range, immune via traits
    b4 = MockBall(4, 50, 0, traits=["electric"])
    # Ball outside range
    b5 = MockBall(5, 200, 200, electric_immunity=False)

    balls = [b1, b2, b3, b4, b5]

    mode.tick(world, balls, delta=1.0) # Tick with 1.0 delta for significant damage

    # Test b1 (affected)
    assert b1.speed_debuff_timer >= 0.5
    assert b1.speed_debuff_multiplier == 0.5
    assert b1.hp == 90.0 # 100 - 10 * 1.0

    # Test b2 (immune via flag)
    assert b2.speed_debuff_timer >= 0.5
    assert b2.speed_debuff_multiplier == 0.5
    assert b2.hp == 100.0 # No damage

    # Test b3 (immune via type)
    assert b3.hp == 100.0

    # Test b4 (immune via trait)
    assert b4.hp == 100.0

    # Test b5 (outside)
    assert b5.speed_debuff_timer == 0.0
    assert b5.hp == 100.0
