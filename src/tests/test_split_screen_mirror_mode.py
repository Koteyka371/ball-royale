import pytest
from ai.game_modes import SplitScreenMirrorMode

class DummyArena:
    def __init__(self):
        self.left = -500
        self.right = 500

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()

class DummyBall:
    def __init__(self, x, hp):
        self.x = x
        self.hp = hp
        self.max_hp = 100.0
        self.speed_multiplier = 1.0
        self.alive = True

def test_split_screen_mirror():
    mode = SplitScreenMirrorMode()
    world = DummyWorld()

    # Mid is 0
    b1 = DummyBall(-200, 100.0) # Left
    b2 = DummyBall(200, 100.0)  # Right

    balls = [b1, b2]
    mode.setup(world, balls)

    assert b1._original_side == "left"
    assert b2._original_side == "right"

    # Stay on original side
    b1.hp = 90.0 # Takes 10 damage
    mode.tick(world, balls, 0.016)
    assert b1.hp == 90.0
    assert b1.speed_multiplier == 1.0

    # Cross side
    b1.x = 200 # Crosses to right
    b1.hp = 80.0 # Takes 10 damage
    mode.tick(world, balls, 0.016)

    assert getattr(b1, "_mirror_inverted") == True
    # Initial diff: 80 - 90 = -10
    # Inverted diff: prev - hp_diff -> 90 - (-10) = 100
    assert b1.hp == 100.0
    assert b1.speed_multiplier == -1.0

    # Take damage again while inverted
    b1.hp = 90.0
    mode.tick(world, balls, 0.016)
    assert b1.hp == 100.0 # Heals instead of taking damage, but capped at max_hp (100)

    # Heal while inverted
    b1.hp = 100.0
    b1.max_hp = 150.0
    mode.tick(world, balls, 0.016)
    assert b1.hp == 100.0

    b1.hp = 110.0 # Heals 10
    mode.tick(world, balls, 0.016)
    # diff = 10. inverted = 100 - 10 = 90.
    assert b1.hp == 90.0

    # Return to original side
    b1.x = -200
    b1.hp = 80.0 # Takes 10 damage
    mode.tick(world, balls, 0.016)
    assert b1.hp == 80.0 # Normal behavior
    assert b1.speed_multiplier == 1.0
