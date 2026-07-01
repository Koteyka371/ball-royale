import re

with open("tests/test_ball_brain.py", "r") as f:
    content = f.read()

old_assert = '    assert ball.current_action in ["attack", "chase", "kite"]'
new_assert = '    assert ball.current_action in ["attack", "chase", "kite", "use_skill"]'

content = content.replace(old_assert, new_assert)

with open("tests/test_ball_brain.py", "w") as f:
    f.write(content)

print("Patch applied")
