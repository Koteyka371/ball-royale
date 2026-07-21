1. **Add `gravity_multiplier_booster` in `src/ai/action.py`**
   - Add a check for `getattr(nearest, "kind", None) == "gravity_multiplier_booster"` in `_get_boosters`.
   - Set `self.ball.gravity_multiplier_timer = 10.0` or similar duration.
   - Clean up booster from `hazards` or `boosters`.
   - Include `gravity_multiplier_booster` in the safe hazard/booster ignore lists for pathing/AI logic.

2. **Add `gravity_multiplier_booster` in `src/ai/action.gd`**
   - Similar to Python implementation, add `"gravity_multiplier_booster"` pickup logic in `_get_boosters`.
   - Set `self.ball.set_meta("gravity_multiplier_timer", 10.0)`.
   - Add to ignore lists.

3. **Apply the immense momentum in `src/ai/action.py`**
   - In the hazard checking loop where `pull_strength` is calculated for `black_hole`, `massive_black_hole`, `gravity_well`, etc., multiply the `pull_strength` by a large amount (e.g. 10.0) if `self.ball.gravity_multiplier_timer > 0`.
   - Decrease `gravity_multiplier_timer -= delta`.

4. **Apply the immense momentum in `src/ai/action.gd`**
   - Perform the same check inside the GDScript hazard processing loop.

5. **Write tests in `src/tests/test_gravity_multiplier_booster.py`**
   - Create a test ensuring the booster is picked up.
   - Create a test ensuring the `pull_strength` or slingshot effect is drastically increased when interacting with a black hole.

6. **Create ideas in `ideas/` directory**
   - Write 2 new game ideas in JSON format.
