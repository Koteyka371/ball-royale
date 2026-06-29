1. Add ModifierZonesMode in `src/ai/game_modes.py`.
   - Setup: Initializes zones of different types (`speed`, `damage`, `heal`).
   - Tick: Applies modifiers to balls inside zones and removes them when outside.
2. Add ModifierZonesMode in `src/ai/game_modes.gd`.
   - Setup and tick logic identical to Python.
3. Add a test script `src/ai/test_modifier_zones.py` to verify the game mode applies modifiers correctly.
4. Run tests with `pytest src/ai/test_modifier_zones.py`.
5. Generate 2 new ideas in `ideas/` directory in JSON format.
6. Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
7. Submit the Pull Request.
