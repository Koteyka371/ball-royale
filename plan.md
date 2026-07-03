1. Add `DailyMutatorMode` in `src/ai/game_modes.py` and `src/ai/game_modes.gd`.
   - Implement `setup()` to randomly select daily extreme global mutators (e.g., 'Low Gravity + Double Damage', 'Invisible Hazards').
   - Keep track of survived balls.
   - Reward cosmetics / bonus skill points to survivors on match end.
2. Register `daily_mutator` in `GAME_MODES` in both Python and GDScript files.
3. Write `src/ai/test_daily_mutator.py` to ensure it applies mutators, tracks survivors, and awards points properly.
4. Run tests and ensure they pass.
5. Create ideas for ideas inbox.
6. Complete pre commit steps.
7. Submit code with branch `idea-486`.
