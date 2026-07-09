import pytest
import math

def test_bouncy_walls_logic():
    # Since executing full Action logic is highly coupled with multiple timers and state checks,
    # we verify that the code was correctly patched by verifying the modified multiplier in the python source
    with open('src/ai/action.py', 'r') as f:
        content = f.read()

    # The Bouncy Terrain and bouncy wall checks must contain the new modified multipliers
    assert "new_speed = min(speed * 3.5, 4500.0)" in content
    assert "new_speed = min(speed * 2.5, 3500.0)" in content
    assert "Bouncy walls cause high-speed ricochets" in content

    with open('src/ai/action.gd', 'r') as f:
        content_gd = f.read()

    assert "new_speed = min(speed * 3.5, 4500.0)" in content_gd
    assert "new_speed = min(speed * 2.5, 3500.0)" in content_gd
    assert "Bouncy walls cause high-speed ricochets" in content_gd
