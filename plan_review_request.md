1. **Modify `src/ai/action.py`**
   - The user task is: "A booster that places a temporary reflection barrier on the ball, deflecting projectiles back at their origin rather than just absorbing them."
   - The codebase currently has `projectile_reflect_booster` which *deals instant damage back to the attacker* without spawning a projectile:
     ```python
     if getattr(target, "projectile_reflect_active", False) and is_ranged:
         original_damage = getattr(attacker, "damage", 10.0)
         if hasattr(attacker, "take_damage"): attacker.take_damage(original_damage)
     ```
   - The prompt explicitly asks for "deflecting projectiles back at their origin rather than just absorbing them" which could mean returning a suspended projectile so it takes time to travel back.
   - Wait, if we suspend the projectile, the attacker can dodge it. If it's just `attacker.take_damage(original_damage)`, it's a hitscan reflect.
   - Let's change the reflection logic to create a suspended projectile targeting the attacker from the target's position.
   - We will append to `target.suspended_projectiles` (or `attacker.suspended_projectiles` if we want it to belong to the attacker? Actually, it should be fired AT the attacker, so we could add it to `attacker.suspended_projectiles` but set `x, y` to the target's position, and target the attacker. This matches how suspended projectiles work: they belong to the shooter, but since it's reflected, maybe we give it to `target.suspended_projectiles`).

Let me verify how suspended projectiles are structured:
```python
attacker.suspended_projectiles.append({
    "x": attacker.x, "y": attacker.y,
    "target": target,
    "damage": final_damage,
    "speed": 600.0,
    "type": "..."
})
```
So we can change the `projectile_reflect_active` logic to spawn a reflected projectile:
```python
        if getattr(target, "projectile_reflect_active", False) and is_ranged:
            if not hasattr(target, "suspended_projectiles"):
                target.suspended_projectiles = []

            target.suspended_projectiles.append({
                "x": target.x,
                "y": target.y,
                "target": attacker,
                "damage": getattr(attacker, "damage", 10.0),
                "speed": 600.0,
                "type": "reflected_projectile"
            })

            if hasattr(self.world, "events"):
                self.world.events.append({'type': 'visual_effect', 'data': {'type': 'shield_block', 'x': target.x, 'y': target.y}})
            return
```
And make the corresponding change in `src/ai/action.gd`.

2. **Modify `src/ai/action.gd`**
   - In `_attempt_damage`, update the `projectile_reflect_active` block:
     ```gdscript
		if has_projectile_reflect and is_ranged_attack:
			var base_dmg_refl = 10.0
			if "damage" in attacker: base_dmg_refl = float(attacker.damage)

            var sus_proj = []
            if typeof(target) == TYPE_DICTIONARY and target.has("suspended_projectiles"):
                sus_proj = target["suspended_projectiles"]
            elif typeof(target) == TYPE_OBJECT and target.has_method("has_meta") and target.has_meta("suspended_projectiles"):
                sus_proj = target.get_meta("suspended_projectiles")
            elif typeof(target) == TYPE_OBJECT and "suspended_projectiles" in target:
                sus_proj = target.suspended_projectiles

            sus_proj.append({
                "x": t_x2,
                "y": t_y2,
                "target": attacker,
                "damage": base_dmg_refl,
                "speed": 600.0,
                "type": "reflected_projectile"
            })

            if typeof(target) == TYPE_DICTIONARY:
                target["suspended_projectiles"] = sus_proj
            elif typeof(target) == TYPE_OBJECT and target.has_method("set_meta"):
                target.set_meta("suspended_projectiles", sus_proj)
            elif typeof(target) == TYPE_OBJECT and "suspended_projectiles" in target:
                target.suspended_projectiles = sus_proj

			if world != null and "events" in world:
				world.events.append({"type": "visual_effect", "data": {"type": "shield_block", "x": t_x2, "y": t_y2}})
			return
     ```

3. **Tests**
   - The test `tests/test_projectile_reflect.py` I just added will fail because the attacker won't take instant damage anymore. I will update it to advance the action tick and verify the attacker takes damage after the projectile travels back.

4. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
5. **Submit PR using `submit` tool**
