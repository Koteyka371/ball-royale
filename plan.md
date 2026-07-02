1.  **Add `invert_booster` to Procedural Generation**
    *   Update `src/arena/procedural_arena.py` and `src/arena/procedural_arena.gd` to include `invert_booster` in random hazard selection.
    *   Update `src/arena/test_procedural_arena.py` to allow the new `invert_booster`.
2.  **Add Booster Collection Logic in Python (`src/ai/action.py`)**
    *   In `_update_skill_timer`, decrement `invert_timer`.
    *   In `_collect_booster`, when collecting an `invert_booster`, find all balls on the opposing team and set their `invert_timer` to 5.0 seconds. Remove the collected booster from the arena hazards and boosters list.
    *   In movement logic (`_chase`, `_flee`, `_escort`, `_hide_behind`, `_group_attack`, etc., wherever `step = speed * delta * 60.0` or similar is calculated for direct movement), check if `invert_timer > 0`. If so, negate `step` (`step = -step`).
3.  **Add Booster Collection Logic in GDScript (`src/ai/action.gd`)**
    *   Replicate the Python logic in `action.gd`. Decrement `invert_timer`, apply to enemies on collection, and invert `step` in movement functions.
4.  **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
5.  **Submit changes**
    *   Commit changes and submit PR for `idea-395`.
