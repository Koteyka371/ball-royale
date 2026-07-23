import re

file_path = "src/ai/action.py"
with open(file_path, "r") as f:
    content = f.read()

pullable_list_str = '["event_horizon_trap", "repulsion_zone", "healing_spring", "booster", "defensive_shield", "personal_safe_zone", "drone_item"'
pullable_list_new = '["deployable_proximity_mud_puddle", "event_horizon_trap", "repulsion_zone", "healing_spring", "booster", "defensive_shield", "personal_safe_zone", "drone_item"'
content = content.replace(pullable_list_str, pullable_list_new)

with open(file_path, "w") as f:
    f.write(content)
