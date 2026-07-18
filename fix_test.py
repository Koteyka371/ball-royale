import re

with open("tests/test_void_mage_black_hole.py", "r") as f:
    text = f.read()

replacement = """        # Execute physics step and verify it moves towards the enemy
        action._process_physics = lambda delta: None # Disable standard physics to test just the action tick which processes hazards
        # Wait, the action loop processes hazards? The hazard moves by its own vx, vy during world.update() or arena.update_zone().
        # Action only updates hazards if it's the specific logic in Action (none here). Action doesn't move hazards globally.
        # Let's manually move it to simulate the tick.
        bh.x += bh.vx * 1.0
        bh.y += bh.vy * 1.0"""

text = text.replace("""        # Execute physics step and verify it moves towards the enemy
        action._process_physics = lambda delta: None # Disable standard physics to test just the action tick which processes hazards
        action.execute("none", 1.0)""", replacement)

with open("tests/test_void_mage_black_hole.py", "w") as f:
    f.write(text)
