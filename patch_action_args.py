# Fix the signature mismatch _apply_obstacle_avoidance(nx_m, ny_m, target_enemy)
# Wait, let's verify what the actual signatures are in action.py and action.gd

with open("src/ai/action.py", "r") as f:
    py_content = f.read()

with open("src/ai/action.gd", "r") as f:
    gd_content = f.read()

print("PY Avoid in hide_behind:", "nx_m, ny_m = self._apply_obstacle_avoidance(nx_m, ny_m, target_enemy)" in py_content)
print("GD Avoid in hide_behind:", "var avoid = _apply_obstacle_avoidance(nx_m, ny_m, target_enemy)" in gd_content)
