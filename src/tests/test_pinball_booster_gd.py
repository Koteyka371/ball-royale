import pytest
import re

def test_pinball_booster_gd():
    with open("src/ai/action.gd", "r") as f:
        content = f.read()

    assert "pinball_booster" in content
    assert "is_frictionless" in content
    assert "skill_silenced" in content
    assert "knockback_multiplier_outgoing" in content
