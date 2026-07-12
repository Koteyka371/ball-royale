from ai.ball_types_hologram import Hologram
import pytest

def test_hologram_bonus():
    h = Hologram(1, 0, 0)
    assert h.BALL_TYPE == "hologram"
