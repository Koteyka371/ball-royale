1. **Refactor the `WeatherChaosMode` altar logic in `src/ai/game_modes.py`:**
   - Change `altars` dict structure slightly (e.g. rename `owner` to `controlling_team`, or add a `capture_max` attribute).
   - Modify the way capture progress is updated. Instead of `altar["capture_progress"] = min(100.0, ...)`, use a variable like `altar["max_capture"] = 100.0`.
   - Update the mapping of weather preferences to be more explicitly defined in a dictionary rather than if/elif blocks, modifying the core requested logic.

2. **Refactor the `WeatherChaosMode` altar logic in `src/ai/game_modes.gd`:**
   - Apply the equivalent semantic refactoring to GDScript. Use a dictionary for weather preferences and rename the capture variables.

3. **Update tests in `src/ai/test_weather_chaos_altar.py`:**
   - Update `altar["owner"]` to `altar["controlling_team"]` if renamed.

4. **Add 2 new ideas in `ideas/idea_idea-741_1.json` and `ideas/idea_idea-741_2.json`**.
5. **Run Pre-Commit steps and Submit PR**.
