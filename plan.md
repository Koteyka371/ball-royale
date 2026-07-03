1.  **Identify where to apply the speed reduction:**
    In `src/ai/action.py` and `src/ai/action.gd`, there's logic that calculates `base_speed`. I will add a check for the `magnetic_boots` cosmetic and apply a 10% reduction (multiply by 0.9) to `base_speed`.

2.  **Identify where to apply the pushback/knockback reduction:**
    In `src/ai/action.py` and `src/ai/action.gd`, there are places where `knockback_force`, `push_strength`, or similar variables are applied (e.g., in `_apply_hazards` and `_handle_collisions`). I will add checks for the `magnetic_boots` cosmetic and reduce the pushback distance/force by 50% (multiply by 0.5) when it's applied to `self.ball`.

3.  **Update `src/ai/action.py`:**
    *   Find the initialization of `base_speed` (around line 1005). Apply `-10%` if `cosmetic == "magnetic_boots"`.
    *   Find the `knockback_force` calculation for hazards (e.g., spikes/explosions around line 2143).
    *   Find the `push_strength` for other hazards (e.g., around line 1816, 1840, 1976).
    *   Find the `knockback_multiplier` for collisions (around line 5731) and reduce by 50% if the ball has `magnetic_boots`.

4.  **Update `src/ai/action.gd`:**
    *   Perform analogous changes in `src/ai/action.gd` to match the Python implementation.
    *   `base_speed` initialization is around line 1696.
    *   `knockback_force` is around line 3307.
    *   `knockback_multiplier` in collisions is around line 9304.
    *   Other push/knockback effects from hazards.

5.  **Write Tests:**
    *   Create a test file `src/ai/test_magnetic_boots.py` to ensure `magnetic_boots` cosmetic reduces base speed and pushback correctly.

6.  **Ideas Inbox:**
    *   Generate two ideas and place them in the `ideas/` directory.

7.  **Pre-commit checks & Submission:**
    *   Run `pytest` to make sure nothing is broken.
    *   Follow the pre-commit instructions.
    *   Submit the code with `gh pr create` as instructed.
