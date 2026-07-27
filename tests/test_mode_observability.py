"""
Pytest integration for physical mode observability.
Tests that all registered game modes pass spatial, collision, and containment simulation checks.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.game_modes import GAME_MODES # type: ignore
from scripts.test_physical_modes import PhysicalModeTester # type: ignore


@pytest.mark.parametrize("mode_key", list(GAME_MODES.keys()))
def test_game_mode_physical_observability(mode_key):
    mode_obj = GAME_MODES[mode_key]
    tester = PhysicalModeTester(ticks_per_mode=50, num_balls=8)
    res = tester.test_mode_physics(mode_key, mode_obj)
    assert res["passed"], f"Game mode '{mode_key}' failed physical observability check: {res['errors']}"
