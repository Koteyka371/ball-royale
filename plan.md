1. **Explore Codebase for "is_night" and game modes.**
2. **Create `DayNightCycleMode` inside `src/ai/game_modes.py` and `src/ai/game_modes.gd`.**
    - Ensure it cycles `world.arena.is_night` between `True` and `False` every 10 seconds.
3. **Register `DayNightCycleMode` in the `GAME_MODES` dictionary.**
    - Add it to both `src/ai/game_modes.py` and `src/ai/game_modes.gd`.
4. **Create a test function `test_day_night_cycle_mode_tick` in `src/ai/test_game_modes.py`.**
    - The existing `is_night` buffs are correctly implemented inside `action.py`/`action.gd` and handle Paladin/Guardian/Assassin/Phantom accordingly.
5. **Invent two new ideas and save to `ideas/`.**
    - Handled via JSON strings.
6. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
7. **Commit, push, and create PR using the `submit` tool.**
