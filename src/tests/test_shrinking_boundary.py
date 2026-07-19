import pytest
from ai.game_modes import ShrinkingBoundaryMode

class MockBall:
    def __init__(self, x, y, hp=100.0, alive=True, ball_type="player"):
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = alive
        self.ball_type = ball_type
        self.killer = ""

        self.max_stamina = 100.0
        self.stamina = 100.0
        self.base_speed = 50.0
        self.speed = 50.0
        self.base_damage = 10.0
        self.original_base_damage = 10.0
        self.traits = []
        self.weather_immunity_timer = 0.0
        self.in_mirror_dimension = False
        self.intangible = False

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_shrinking_boundary_damage():
    mode = ShrinkingBoundaryMode()
    world = MockWorld()
    ball_in = MockBall(500, 500)
    ball_out = MockBall(-10, 500)
    ball_spectator = MockBall(-10, 500, ball_type="spectator")
    balls = [ball_in, ball_out, ball_spectator]

    mode.setup(world, balls)

    # Tick with a large delta to deal damage
    mode.tick(world, balls, delta=1.0)

    # Ball inside should be untouched
    assert ball_in.hp == 100.0
    assert ball_in.alive == True

    # Ball outside should take damage (10.0 per second)
    assert ball_out.hp == 90.0
    assert ball_out.alive == True

    # Spectator should be untouched
    assert ball_spectator.hp == 100.0

def test_shrinking_boundary_elimination():
    mode = ShrinkingBoundaryMode()
    world = MockWorld()
    # Give ball very low hp
    ball_out = MockBall(-10, 500, hp=5.0)
    balls = [ball_out]

    mode.setup(world, balls)

    # Tick with 1.0 delta (deals 10 damage, which is > 5 hp)
    mode.tick(world, balls, delta=1.0)

    # Ball should be dead
    assert ball_out.hp == 0.0
    assert ball_out.alive == False
    assert ball_out.killer == "Shrinking Boundary"
