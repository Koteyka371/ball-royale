import pytest

def test_hazard_lines_spawning():
    from ai.game_modes import GAME_MODES
    assert "hazard_lines" in GAME_MODES

    mode = GAME_MODES["hazard_lines"]

    class MockArena:
        def __init__(self):
            self.width = 1000.0
            self.height = 1000.0
            self.hazards = []

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()

    class MockBall:
        def __init__(self):
            self.x = 500.0
            self.y = 500.0
            self.hp = 100.0
            self.alive = True

        def take_damage(self, dmg):
            self.hp -= dmg

    world = MockWorld()
    ball = MockBall()
    balls = [ball]

    mode.setup(world, balls)

    # Tick 0.1s to spawn the first hazard (initial spawn_timer = 0.1)
    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert getattr(hazard, "kind") in ["hazard_line_vertical", "hazard_line_horizontal"]
    assert getattr(hazard, "damage") == 20.0
    assert getattr(hazard, "radius") == 50.0

    # Force hazard onto ball
    hazard.x = ball.x
    hazard.y = ball.y
    if getattr(hazard, "kind") == "hazard_line_vertical":
        setattr(hazard, "vx", 0)
        setattr(hazard, "vy", 0)
    else:
        setattr(hazard, "vx", 0)
        setattr(hazard, "vy", 0)

    # Tick again to apply damage
    mode.tick(world, balls, 1.0)

    # Check if damage was applied (20.0 * 1.0)
    assert ball.hp == 80.0
