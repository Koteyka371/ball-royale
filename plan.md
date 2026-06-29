1. **Add `magnet_powerup` generation in `src/arena/procedural_arena.py` and `src/arena/procedural_arena.gd`**:
   - Update the hazard generation logic in `ProceduralArena.generate()` to occasionally spawn `magnet_powerup` with `damage = 0.0`. I'll also add it to `test_procedural_arena.py` hazard assertions.
2. **Implement powerup collection in `src/ai/action.py` and `src/ai/action.gd`**:
   - In the item collection logic (where `drone_item`, `emp_item` etc. are checked), add a check for `magnet_powerup`.
   - When collected, set a property `has_magnet = True` and a timer `magnet_timer = 15.0` on the ball. Remove the powerup from the arena hazards.
3. **Add magnet pulling effect in physics execution in `src/ai/action.py` and `src/ai/action.gd`**:
   - In `Action.execute()`, check if `self.ball.has_magnet` is true and `magnet_timer > 0`. If so, decrease the timer.
   - While active, iterate over all hazards in `self.world.arena.hazards` and other balls' items. If a hazard/item is within a certain radius (e.g. 200.0) and is considered small/pullable (like small hazards, drone_items, powerups, etc.), apply a small velocity or direct position shift towards the player.
   - For python, modify hazard `x` and `y` towards the ball. Note: Hazards might not have velocity in base implementation, so I'll move them slightly every tick. I'll focus on items with `damage == 0` or certain kinds. Let's pull ALL smaller hazards/items or those with radius < 30.
4. **Update `src/ai/perception.py` and `src/ai/perception.gd`**:
   - Ensure `magnet_powerup` is categorized as a booster so AI knows it's an item to collect.
5. **Add tests**:
   - Add a test in `src/ai/test_action_advanced.py` to verify the magnet timer decreases and pulls nearby items.
6. **Complete pre-commit steps**:
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
7. **Submit changes**:
   - Push and open a PR.
   - Add 2 ideas JSONs into `ideas/`.
