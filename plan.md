1.  **Understand Requirements:**
    *   **Trigger:** When a ball is dashing (`is_dashing`), it leaves a trail.
    *   **Trail:** Matches the ball's current cosmetic aura color (`cosmetic_aura_color`).
    *   **Effect 1 (Different Color):** Stepping on a trail of a *different* color causes a short stun (`stun_timer`).
    *   **Effect 2 (Same Color):** Stepping on a trail of the *same* color grants a temporary speed boost (e.g., modifying `speed` and storing original speed).
2.  **Implementation Details (Python - `src/ai/game_modes.py`):**
    *   Create `DashAuraTrailMutatorMode(GameMode)`.
    *   `setup()`: Give all balls a random `cosmetic_aura_color` if they don't have one to ensure the mode works even without prior setup.
    *   `tick()`:
        *   Store `_orig_speed` if not present.
        *   Handle active speed buffs (e.g., `aura_speed_buff_timer`). If timer > 0, `b.speed = b._orig_speed + 150`, else `b.speed = b._orig_speed`. Ensure cleanup.
        *   Track `is_dashing = getattr(b, "is_dashing", False)`.
        *   If `is_dashing`, check `last_trail_spawn_time`. If enough time passed (e.g. 0.05s), spawn `AuraTrailHazard`.
        *   The hazard needs to be added to `world.arena.hazards` or tracked internally in the mutator. It's better to add to a custom list in `world` or `world.arena.hazards` if it acts as a generic hazard, but a local list in the mutator or attaching to `world` is safer to avoid engine assumptions. Actually, many mutators track custom hazards in `self.trails = getattr(world, 'aura_trails', [])`. Let's just track them in `world.aura_trails`.
        *   Iterate over `world.aura_trails`. Reduce their `life_timer`. Remove if `<= 0`.
        *   For each active ball and each trail:
            *   Calculate distance. If `dist < ball.radius + trail.radius`:
            *   Compare `ball.cosmetic_aura_color` and `trail.color`.
            *   We need to handle tuples/lists for colors properly. Compare them.
            *   Apply stun or speed boost buff timer.
3.  **Implementation Details (GDScript - `src/ai/game_modes.gd`):**
    *   Same logic as Python. Create `DashAuraTrailMutatorMode`.
    *   Track trails in `world.get_meta("aura_trails")`.
    *   Ensure proper type checking for arrays/colors.
4.  **Registration:**
    *   Add to `GAME_MODES` in both files.
5.  **Tests:**
    *   Create `src/tests/test_dash_aura_trail_mode.py`.
    *   Test setup (colors initialized).
    *   Test trail generation when `is_dashing = True`.
    *   Test stun when stepping on different color.
    *   Test speed boost when stepping on same color.
6.  **Pre-commit checks & Submission.**
