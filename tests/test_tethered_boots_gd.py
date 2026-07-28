import pytest

def test_tethered_boots_gd_implemented():
    with open("src/ai/action.gd", "r") as f:
        content = f.read()

    assert "cosmetic_val == \"tethered_boots\":" in content
    assert "knockback_multiplier *= 0.5" in content
    assert "for a in allies:" in content
    assert "speed_boost_timer" in content
