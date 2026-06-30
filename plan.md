1. **Add `portal_gun` to procedural arena hazards.**
   - Run a Python script via `run_in_bash_session` to insert `elif random.random() < 0.05: kind = "portal_gun"; damage = 0.0` into `update_zone` method of `src/arena/procedural_arena.py` and `src/arena/procedural_arena.gd`.
   - Update `src/arena/test_procedural_arena.py` whitelist using a Python script via `run_in_bash_session` to include `"portal_gun"`.
   - Verify edits using `git diff src/arena/`.

2. **Add `portal_gun` to `perception` class.**
   - Edit `src/ai/perception.py` via Python script to check for `"portal_gun"` alongside `"drone_item"` and `"stealth_drone_item"` to append to the boosters list.
   - Edit `src/ai/perception.gd` via Python script to do the same.
   - Verify edits using `git diff src/ai/perception.*`.

3. **Handle `portal_gun` collection.**
   - Edit `src/ai/action.py` via Python script. In `_collect_booster`, when `getattr(nearest, "kind", None) == "portal_gun"`, append it to `self.ball.inventory` and remove from arena/boosters.
   - Edit `src/ai/action.gd` via Python script. In `_collect_booster`, handle `nearest.kind == "portal_gun"` by updating `get_meta("inventory")` and removing the nearest from hazards.
   - Verify edits using `git diff src/ai/action.*`.

4. **Implement `portal_gun` usage.**
   - Edit `src/ai/action.py` via Python script. Around line 222 (after `exit_portal`), add logic: if strategy is `"flee"` or `"defend"` and `"portal_gun"` is in inventory:
     - Remove `"portal_gun"` from inventory.
     - Generate two new hazard IDs (e.g., `len(hazards) + random.randint(10000, 99999)`).
     - Find a target location (e.g., center of map or opposite side).
     - Create two connected hazards of `kind="teleporter"`.
     - `portal1` at `self.ball.x`, `self.ball.y`.
     - `portal2` at `target_x`, `target_y`.
     - Append both to `self.world.arena.hazards` with duration 10.0.
   - Edit `src/ai/action.gd` via Python script. Do the exact same for GDScript logic.
   - Verify edits using `git diff src/ai/action.*`.

5. **Run test suite.**
   - Execute `PYTHONPATH=src pytest src/` via `run_in_bash_session` to verify tests pass.

6. **Complete pre commit steps.**
   - Complete pre commit steps to ensure proper testing, verification, review, and reflection are done using `default_api:pre_commit_instructions`.

7. **Create Ideas Box JSONs.**
   - Use `run_in_bash_session` to `cat << 'EOF' > ideas/idea_idea-319_1.json` with a valid idea.
   - Use `run_in_bash_session` to `cat << 'EOF' > ideas/idea_idea-319_2.json` with a valid idea.

8. **Submit PR.**
   - Use `run_in_bash_session` to run `git add .`, `git commit -m "Add Portal Gun item"`, `git push origin idea-319`, and `gh pr create --title '[idea-319] Add Portal Gun item' --body 'Task: idea-319' --label 'automated'`.
