1. **Implement `energy_shield` skill logic in Python (`src/ai/action.py`)**
   - In `_use_skill`, handle `skill_name == "energy_shield"`. Activate it by setting `energy_shield_active = True` and `energy_shield_timer = 3.0` on `self.ball`.
   - In `_update_skill_timer`, decrement `energy_shield_timer` by `delta`. If it reaches 0 or below, set `energy_shield_active = False`.
   - In `_attempt_damage` (or when dealing damage), if the target has `energy_shield_active`, negate the damage on the target and apply 50% of `original_damage` (or the damage that would have been dealt) back to the attacker. Ensure target takes 0 damage.

2. **Implement `energy_shield` skill logic in GDScript (`src/ai/action.gd`)**
   - Replicate the exact same logic in `_use_skill`, `_update_skill_timer`, and `_attempt_damage`. Ensure we use `.has_method("set_meta")` / `has_meta` / `get_meta` correctly if properties aren't defined.

3. **Add tests for `energy_shield`**
   - Create `src/ai/test_energy_shield.py` testing the 3s timer and the 50% damage reflection in `_attempt_damage`. Verify the target takes 0 damage and attacker takes 50%.
   - Run tests `PYTHONPATH=src pytest` to verify.

4. **IDEAS INBOX**
   - Create two JSON files in `ideas/` with new game features.

5. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
   - Call `pre_commit_instructions` tool.

6. **Submit PR**
   - Stage and commit changes to `idea-469` branch.
   - Create a Pull Request with title `[idea-469] Add Energy Shield skill with damage reflection` and body `Task: idea-469`. Label the PR with 'automated'.
