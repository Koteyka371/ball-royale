import pytest
from src.ai.game_modes import GAME_MODES

def test_hovercraft_mode():
    hovercraft_mode = GAME_MODES.get('hovercraft')
    assert hovercraft_mode is not None
    assert hovercraft_mode.name == "Hovercraft"

    class MockBall:
        def __init__(self):
            self.is_frictionless = False

    ball = MockBall()
    hovercraft_mode.apply_dynamic_traits(None, [ball], 0.1)
    assert ball.is_frictionless is True

    dict_ball = {"is_frictionless": False}
    hovercraft_mode.apply_dynamic_traits(None, [dict_ball], 0.1)
    assert dict_ball["is_frictionless"] is True
