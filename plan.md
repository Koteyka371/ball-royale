1. **Modify `_collect_booster` in `src/ai/action.py`**
   - Use `sed` to insert an `elif` condition for `getattr(nearest, "kind", None) == "bumper_booster"` in `src/ai/action.py`.
   - Set `self.ball.bumper_booster_timer = 5.0`.
   - Check if the `nearest` item exists in `self.world.arena.hazards` and `self.world.boosters`, and if so, remove it.

2. **Modify `_update_skill_timer` in `src/ai/action.py`**
   - Use `sed` to insert a block to decrement `bumper_booster_timer` in `src/ai/action.py`.
   - When the timer is active (>0), iterate through `self.world.balls`, and apply logic similar to `bumper` hazard. For enemies, compute squared distance `dist_sq`. The aura threshold `dist_sq < (b_rad + other_rad + 10.0)**2`. If in range, calculate normal vectors, apply `bounce_strength = 600.0 * delta` to positions, and set velocities `other.vx = nx * 2000.0` and `other.vy = ny * 2000.0`.

3. **Verify `src/ai/action.py` changes**
   - Run `git --no-pager diff src/ai/action.py` to ensure the logic was correctly inserted without syntax errors and whitespace issues.

4. **Modify `_collect_booster` equivalent block in `src/ai/action.gd`**
   - Use `sed` to insert the GDScript block for `bumper_booster` near line `4623` in `src/ai/action.gd` (the collection switch statement).
   - The logic will set `bumper_booster_timer` metadata to `5.0` and remove from `hazards` and `boosters` arrays.

5. **Modify `_update_skill_timer` in `src/ai/action.gd`**
   - Use `sed` to insert the `bumper_booster_timer` decrement logic near the end of `func _update_skill_timer(delta: float):` in `src/ai/action.gd`.
   - Loop through `self.world.balls` safely, check for enemy status, and apply velocity bumps using `get_meta` and `set_meta`.

6. **Verify `src/ai/action.gd` changes**
   - Run `git --no-pager diff src/ai/action.gd` to ensure correct integration.

7. **Create test file for `bumper_booster`**
   - Use `write_file` to create `src/ai/test_bumper_booster.py`.
   - The test will mock world, balls, and booster objects to test both collection logic (timer update and removal) and the aura effect logic (velocity changes on enemy bump).

8. **Verify test file creation**
   - Run `cat src/ai/test_bumper_booster.py` to verify the test file was written correctly.

9. **Generate IDEAS INBOX files**
   - Run bash commands: `mkdir -p ideas`
   - Write two new JSON ideas using `write_file` at `ideas/idea_idea-338-1_1.json` and `ideas/idea_idea-338-1_2.json` with correct schema.
   - Verify files exist using `ls -l ideas/`.

10. **Run all tests**
    - Run command `PYTHONPATH=src pytest src/ai/test_bumper_booster.py` and then the whole test suite `PYTHONPATH=src pytest`.

11. **Pre-commit steps**
    - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

12. **Submit Pull Request**
    - Run bash command `gh pr create --title "[idea-338-1] Add Bumper Aura Booster" --body "Task: idea-338-1" --label "automated"`.
