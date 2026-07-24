import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

def test_heavy_gravity_trap_gd_logic_exists():
    with open("src/ai/action.gd", "r") as f:
        content = f.read()
        assert "elif trap_variant == \"heavy_gravity_well\":" in content
        assert "if hgt > 0.0:" in content
        assert "knockback_multiplier = 0.0" in content
