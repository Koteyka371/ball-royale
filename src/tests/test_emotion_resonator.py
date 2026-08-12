import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_emotion_resonator_capture_and_radiate():
    from ai.game_modes import GameMode

    class DummyBall:
        def __init__(self, id, x, y, emotion):
            self.id = id
            self.x = x
            self.y = y
            self.radius = 15.0
            self.alive = True
            self.ball_type = "player"
            self.emotion = emotion

    class DummyHazard:
        def __init__(self, x, y, kind):
            self.id = 1
            self.x = x
            self.y = y
            self.radius = 40.0
            self.kind = kind
            self.captured_emotion = None
            self.radiate_timer = 0.0

    class DummyArena:
        def __init__(self, hazards):
            self.hazards = hazards

    class DummyWorld:
        def __init__(self, arena):
            self.arena = arena

    b1 = DummyBall(1, 0, 0, "rage")      # Will touch hazard
    b2 = DummyBall(2, 200, 0, "fear")    # Will be in aura
    b3 = DummyBall(3, 1000, 0, "neutral")# Outside aura

    hazard = DummyHazard(0, 0, "emotion_resonator")
    world = DummyWorld(DummyArena([hazard]))

    mode = GameMode()

    # Tick 1: B1 touches hazard, captures "rage"
    mode.apply_dynamic_traits(world, [b1, b2, b3], 0.1)

    assert hazard.captured_emotion == "rage"
    assert hazard.radiate_timer > 0.0

    # Because B1 is first in the list, it captures the emotion.
    # But because the loop checks b2 AFTER b1 captures, b2 might get the radiated emotion in the same tick if we continue.
    # Wait, the code sets it to "rage"
    assert b2.emotion == "rage"

    # B3 is outside, so it should remain neutral
    assert b3.emotion == "neutral"
