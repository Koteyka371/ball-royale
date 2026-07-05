1. **Add `material_magnet_booster` to `procedural_arena.py` & `procedural_arena.gd`**:
   - In `src/arena/procedural_arena.py`, add `"material_magnet_booster"` to the lists of allowed kinds for drop/item hazard types.
   - In `src/arena/procedural_arena.gd`, add `"material_magnet_booster"` to the corresponding lists.
   - Update tests `src/arena/test_procedural_arena.py` to allow `"material_magnet_booster"`.

2. **Update `action.py` to handle `material_magnet_booster` collection & pulling**:
   - Add `"material_magnet_booster"` to the condition that sets a timer. When picked up, set `self.ball.material_magnet_timer = 10.0` (as requested: 10 seconds).
   - In the periodic update loop, if `material_magnet_timer > 0`, reduce it by `delta`. Iterate through items in `world.arena.items`. If an item is a `"material"`, check if the distance is `< 250000` (500 radius squared). If so, pull it towards `self.ball`.

3. **Update `action.gd` to handle `material_magnet_booster` collection & pulling**:
   - Do the exact same thing in GDScript. Add `"material_magnet_booster"` check, set `material_magnet_timer = 10.0`.
   - Iterate through `world.arena.items` if available, checking if they are `"material"` and pull them towards the ball if distance squared `< 250000`.

4. **Write tests for `material_magnet_booster`**:
   - Add test to ensure `material_magnet_booster` sets the timer and pulls materials properly in `test_pull_booster.py` or a new test file `test_material_magnet.py`.

5. **Pre-commit tasks**:
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

6. **Create IDEAS INBOX files**:
   - Create 2 JSON files in `ideas/` with new feature ideas.

7. **Submit**:
   - Push and open PR.
