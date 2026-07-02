1. **Add `PinballArena` to `arena_types.py` and `arena_types.gd`**
   - In `src/arena/arena_types.py` and `src/arena/arena_types.gd`, implement `PinballArena(ProceduralArena)`.
   - The generation logic should place multiple pinball components:
     - `pinball_flipper`: We can implement it as a Hazard with custom metadata (e.g., rotation, angular velocity).
     - `pinball_bumper`: Already in the game, we will scatter them strategically.
     - `pinball_slingshot`: A hazard that imparts huge momentum when touched.
   - Register the arena type in `ARENAS` dictionary/array in both files.

2. **Add Physics Logic for Pinball Hazards in `action.py` and `action.gd`**
   - Update `Action._resolve_collisions` or the main `execute` hazard loop to handle `pinball_flipper` and `pinball_slingshot`.
   - `pinball_flipper`: Apply huge directional knockback if hit while active/triggered.
   - `pinball_slingshot`: Apply massive bounce away from the hazard.
   - Update `bumper` logic if needed to ensure momentum drastically changes trajectory.

3. **Add `update_zone` Logic for Flippers**
   - In `ProceduralArena.update_zone` (or just in `PinballArena.update_zone`), update flippers to "flip" (change angle) periodically or when triggered.

4. **Testing**
   - Add a test `test_pinball_arena.py` that generates `PinballArena`, asserts presence of flippers, slingshots, and bumpers.
   - Add a test for collision with these hazards to verify momentum/knockback changes.

5. **Pre-commit Steps**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

6. **Submit PR**
   - Commit, push, and submit.
