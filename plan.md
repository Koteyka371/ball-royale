1. **Implement `CrimsonFogEventMode` in `src/ai/game_modes.py` and `src/ai/game_modes.gd`.**
   - The game mode needs to set up the fog timer and activate the crimson fog.
   - When active, players should continuously lose health over time (e.g. `10.0 * delta`).
   - We will set a boolean `crimson_fog_active` on `world.arena` or `world.game_mode` when the fog is active, and apply a visual effect if possible. Wait, `world.game_mode.crimson_fog_active` is sufficient, or just check `game_mode.name == "Crimson Fog Event"` and its `fog_active` state.

2. **Hook into the damage resolution logic in `src/ai/action.py` and `src/ai/action.gd`.**
   - In `action.py`, locate the `if new_hp < old_hp:` block inside `_deal_damage` or wherever it occurs in `execute()`. Add logic that checks if the current game mode is Crimson Fog Event and if `fog_active` is True. If so, apply double lifesteal (restore `2.0 * damage_dealt` to the attacker).
   - In `action.gd`, locate the corresponding `if new_hp < old_hp:` block (around line 2844) inside `_attempt_damage_internal` and do the same: check if `world.game_mode` is Crimson Fog Event and `fog_active` is true. Restore `2.0 * damage_dealt` to the attacker.

3. **Register the game mode.**
   - Add `"crimson_fog_event": CrimsonFogEventMode()` to the `GAME_MODES` dictionary in `src/ai/game_modes.py`.
   - Add `"crimson_fog_event": CrimsonFogEventMode.new()` to the `GAME_MODES` dictionary in `src/ai/game_modes.gd`.

4. **Add Pytest unit tests in `src/tests/test_crimson_fog_event.py`.**
   - Test that `CrimsonFogEventMode` damages players over time when `fog_active` is true.
   - Test that an attacker dealing damage inside the fog restores double the damage as HP.
   - Test that the fog activates/deactivates properly based on timer.

5. Complete pre commit steps to ensure proper testing, verification, review, and reflection are done.

6. Submit the PR using `submit`.
