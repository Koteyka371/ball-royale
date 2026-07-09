1. **Add `projectile_reflect_booster` to game modes**
   - Update `src/ai/game_modes.py` to add `"projectile_reflect_booster"` to `booster_kinds`.
   - Update `src/ai/game_modes.gd` to add `"projectile_reflect_booster"` to `booster_kinds`.
2. **Implement collection logic in Python**
   - In `src/ai/action.py`, inside `_collect_booster`, add an `elif getattr(nearest, "kind", None) == "projectile_reflect_booster":` block.
   - Set `self.ball.projectile_reflect_active = True` and `self.ball.projectile_reflect_timer = 5.0` (or some duration). Remove the booster from arena hazards and world boosters.
   - In the `execute` method of `src/ai/action.py`, decrement `projectile_reflect_timer` and turn off `projectile_reflect_active` when it reaches <= 0.
3. **Implement collection logic in GDScript**
   - In `src/ai/action.gd`, inside `_collect_booster`, add an `elif "kind" in nearest and nearest.kind == "projectile_reflect_booster":` block.
   - Use `self.ball.set_meta("projectile_reflect_active", true)` and `self.ball.set_meta("projectile_reflect_timer", 5.0)` (or equivalent depending on dictionary vs object). Remove the booster appropriately.
   - In the `execute` method of `src/ai/action.gd`, decrement the timer and disable the effect when it expires.
4. **Implement effect logic in Python (`_attempt_damage`)**
   - In `src/ai/action.py`, modify `_attempt_damage` where `is_ranged` is evaluated.
   - After determining it is a ranged attack (`if is_ranged:`), check `if getattr(target, "projectile_reflect_active", False):`.
   - If active, reflect the damage back to the attacker using `if hasattr(attacker, "take_damage"): attacker.take_damage(original_damage)` (or `world._deal_damage` if appropriate), spawn a visual effect, and `return` to prevent damage to the target.
5. **Implement effect logic in GDScript (`_attempt_damage`)**
   - In `src/ai/action.gd`, modify `_attempt_damage`.
   - Under `if is_ranged_attack:`, check `if target.get("projectile_reflect_active", false)` (or `get_meta`).
   - If active, damage the attacker and return.
6. **Pre-commit step**
   - Run `pre_commit_instructions` and address metrics, tests, etc. Include the IDEAS INBOX step.
