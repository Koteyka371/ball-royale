1. **Implement `ModifierSafeZoneMode` class in `src/ai/game_modes.py` and `src/ai/game_modes.gd`**
   - Inherit from `GameMode`.
   - Setup state: initialize a safe zone that shrinks over time.
   - Setup a `modifier_timer` that periodically triggers a random modifier.
   - When triggered, pick a random modifier (buff or debuff) and apply it to all balls inside the safe zone (e.g. speed boost, damage boost, slow, damage taken).

2. **Add `ModifierSafeZoneMode` to `GAME_MODES`**
   - Register it as `modifier_safe_zone` in both `src/ai/game_modes.py` and `src/ai/game_modes.gd`.

3. **Add tests for `ModifierSafeZoneMode`**
   - Create `test_modifier_safe_zone.py`.
   - Test that the safe zone shrinks.
   - Test that modifiers are applied periodically to balls inside the safe zone.
   - Test that balls outside the safe zone are not affected by the modifiers but take zone damage instead.

4. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
   - Run tests (`pytest`)
   - Check standard requirements

5. **Generate Ideas**
   - Create two JSON files in `ideas/` with new game features.

6. **Submit**
   - Create branch, commit, push, create PR.
