import pytest
from ai.game_modes import GameMode, EchoMode
import copy

class MockBall:
    def __init__(self, id, team, x, y):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.is_casting = False
        self.skill_target = None
        self.cd_timer = 0.0

    def duplicate(self):
        return copy.copy(self)

class MockWorld:
    pass

def test_echo_mode_mechanics():
    mode = EchoMode()
    world = MockWorld()
    b1 = MockBall("b1", "red", 100.0, 100.0)
    b2 = MockBall("b2", "blue", 200.0, 200.0)
    balls = [b1, b2]

    # Tick 1: Record Phase (timer = 0.1)
    b1.x = 101.0
    mode.tick(world, balls, 0.1)

    # Tick 2: Record Phase (timer = 0.2)
    b1.x = 102.0
    mode.tick(world, balls, 0.1)

    assert "b1" in mode.history
    assert len(mode.history["b1"]) == 2
    assert mode.history["b1"][0]["x"] == 101.0
    assert mode.history["b1"][1]["x"] == 102.0

    # Fast forward to playback phase (timer = 10.1)
    mode.timer = 10.0
    mode.tick(world, balls, 0.1)

    # Echoes should be created
    assert len(balls) == 4
    echo_b1 = next(b for b in balls if getattr(b, "is_echo", False) and b.id == "b1_echo")

    # Tick 1 of playback should set echo to history index 0
    assert echo_b1.x == 101.0

    # Tick 2 of playback (timer = 10.2)
    mode.tick(world, balls, 0.1)
    assert echo_b1.x == 102.0

    # Fast forward to next cycle (timer = 20.1)
    mode.timer = 20.0
    mode.tick(world, balls, 0.1)

    # Echoes should be cleaned up
    assert len(balls) == 2
    assert len(mode.echoes) == 0
    assert len(mode.history) == 2  # It records the current tick
