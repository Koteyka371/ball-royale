1. **Modify `ExtremeWeatherMode` in `src/ai/game_modes.py` and `src/ai/game_modes.gd`**
   - Locate the `acid_rain` weather tick logic.
   - Update it to degrade max HP and armor for metallic/heavily armored balls.
   - Check for `"metal"` or `"armor"` in the ball's type or traits. If present, instead of just taking damage, reduce `max_hp` and set a `defense_multiplier` penalty or `acid_debuff_timer`.
   - Also occasionally spawn `neutralizing_puddle` or `water_puddle` hazards during `acid_rain`.
2. **Read modified files to verify edits**
3. **Add "water_puddle" hazard effect in `src/ai/action.py` and `src/ai/action.gd`**
   - Find where puddle effects are handled in `action.py`/`action.gd`.
   - In `water_puddle` or a new `neutralizing_puddle` block, restore `max_hp` back up to `base_max_hp` (or by a certain amount per tick) and clear `acid_debuff_timer` / restore `defense_multiplier`.
4. **Read modified files to verify edits**
5. **Update tests**
   - Add tests for `acid_rain` armor degradation and neutralizing puddles in `src/ai/test_extreme_weather.py`.
   - Run tests `PYTHONPATH=.:src:src/ai pytest tests/ src/ai/test_extreme_weather.py`.
6. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
7. **Commit, generate ideas files, push and submit PR**
   - Generate two ideas in the `ideas/` directory.
   - Use `git checkout -b idea-983`, `git commit`, push branch, and submit PR.
