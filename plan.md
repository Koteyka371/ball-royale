1. **Implement `InfectionAuraMode` in `src/ai/game_modes.py`**:
   - Create `InfectionAuraMode` inheriting from `GameMode`.
   - In `setup`, pick a random valid ball to start as infected (`b.is_infected = True`).
   - In `tick`, iterate over balls, deal damage to infected balls, and if any uninfected ball is near an infected ball for 2 or more seconds, it becomes infected.
   - Register the mode in `GAME_MODES["infection_aura"]`.
2. **Implement `InfectionAuraMode` in `src/ai/game_modes.gd`**:
   - Apply exactly the same logic via a new `InfectionAuraMode` class extending `GameMode`, safely accessing properties (whether instances or dictionaries) using `.get()`, `has_meta()`, etc., according to GDScript conventions.
   - Register it via `GAME_MODES["infection_aura"]`.
3. **Verify Functionality**:
   - Review modifications to ensure correct implementation for `src/ai/game_modes.py` and `src/ai/game_modes.gd`.
   - Check if `src/tests/test_infection_aura.py` executes successfully.
4. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
5. **Submit via PR**.
