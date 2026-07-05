import re
with open("src/ai/test_ice_patch.py", "r") as f:
    code = f.read()

new_code = code.replace(
"""    # Expect bounce to have larger speed multiplier
    speed = math.sqrt(ball._reflection_vx**2 + ball._reflection_vy**2)
    assert speed >= 200.0 # Bounced on wall, should be 2.0 multiplier of current speed (which includes the added vx)""",
"""    # Expect bounce to have larger speed multiplier
    # Execute removes _reflection_vx and applies it to vx
    speed = math.sqrt(ball.vx**2 + ball.vy**2)
    assert speed >= 200.0 # Bounced on wall, should be 2.0 multiplier of current speed (which includes the added vx)""")

with open("src/ai/test_ice_patch.py", "w") as f:
    f.write(new_code)
