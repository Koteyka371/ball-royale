1. **Add `booster_trap_item` to `GameMode` spawn pools:**
   - In `src/ai/game_modes.py` and `src/ai/game_modes.gd`, add `"booster_trap_item"` to the `booster_kinds` arrays.
2. **Implement `booster_trap_item` pick-up logic in `Action.execute()`:**
   - In `src/ai/action.py` and `src/ai/action.gd` (`_collect_booster` logic):
     - When `nearest.kind == "booster_trap_item"`, append `"booster_trap"` to `ball.inventory`.
     - Remove the item from `world.arena.hazards` and `world.boosters`.
3. **Implement `booster_trap` deployment logic in `Action.execute()`:**
   - In `src/ai/action.py` and `src/ai/action.gd`:
     - If `"booster_trap"` is in `ball.inventory` (and optionally the strategy is `flee` or `defend`), deploy it.
     - Deploy it by spawning a hazard/entity named `"booster_trap"` or `"placed_booster_trap"` at the ball's coordinates.
     - Set the `duration` (or have infinite duration), `owner_id`, and make it look like a regular booster (e.g., set `active = True`).
     - Remove `"booster_trap"` from `ball.inventory`.
4. **Implement `placed_booster_trap` interaction logic:**
   - Modify the `_collect_booster` function in `src/ai/action.py` and `src/ai/action.gd` to detect when a ball picks up `"placed_booster_trap"`.
   - If the ball picking it up is an enemy (different `id` than `owner_id` / different team), apply a random negative status effect (poison, freeze, stun, or slow).
   - If the ball is the owner, maybe just ignore or give back the item (let's assume it explodes/triggers on enemies).
   - Remove the `placed_booster_trap` from the arena.
5. **Update exclusion lists for hazard targets/pull abilities:**
   - Add `"booster_trap_item"` and `"placed_booster_trap"` to the various hazard filter lists in `action.py` and `action.gd` (where items like `"placeable_trap_item"` are listed).
6. **Write tests:**
   - Create a test file `tests/test_booster_trap.py` that checks the item is picked up, placed, and triggers negative effects on an enemy.
7. **Complete pre-commit steps:**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
8. **Generate features and Submit PR:**
   - Generate two ideas in `ideas/` directory.
   - Use the `submit` tool to create PR.
