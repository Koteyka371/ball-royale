1. **Modify `src/ai/action.py`**
   - Locate the logic where a trap hazard is triggered (`elif trap_variant == "emp":`).
   - Instead of just applying EMP effects to the single ball that stepped on it, iterate through all balls in the world.
   - If a ball is within a "huge radius" (e.g., `800.0`, same as `emp_booster`), check for `emp_immunity_timer`.
   - If not immune, disable shields (`b.shield = 0.0`), reset positive buffs (speed and damage multipliers), and apply the EMP status (`is_emped = True`, `emp_timer = 2.0`, `skill_timer` increased).
   - The trap itself should be destroyed (`hazard.duration = 0.0`) after triggering.

2. **Modify `src/ai/action.gd`**
   - Mirror the changes from Python to GDScript.
   - Locate `elif trap_variant == "emp":` inside the loop for trap collision.
   - Iterate through `self.world.balls` using a distance check (`800.0 * 80.0`).
   - For each ball in range without EMP immunity, set `is_emped = true`, `emp_timer = 2.0`, disable shields, reset speed/damage multipliers, and increase `skill_timer`.
   - Set the hazard's duration/active state to 0 / false to destroy it.

3. **Add Tests**
   - Create a test in `tests/test_emp_trap_radius.py` (or similar) to verify that stepping on an `emp` trap disables shields and buffs for multiple players in the radius.

4. **Complete Pre Commit Steps**
   - Run tests, check coverage, and clean up.

5. **Generate Ideas**
   - Create two JSON files in the `ideas/` directory with new feature ideas.

6. **Submit Pull Request**
   - Commit changes.
   - Create PR with the specified branch and labels.
