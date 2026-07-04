1. **Verify setup:** We have already modified `src/arena/procedural_arena.py`, `src/arena/procedural_arena.gd`, `src/ai/game_modes.py`, and `src/ai/game_modes.gd`.
   These changes include:
   - Introducing `decoy_spawner` in the procedural arenas.
   - Spawning logic and movement mimicking logic in the Battle Royale mode (`game_modes.py` and `game_modes.gd`).
   - I have tested the logic with `test_decoy_spawner.py` and confirmed it works.

2. **Run tests:**
   - Execute `PYTHONPATH=src pytest src/` to verify that everything still works properly without any test regressions.

3. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**

4. **Submit final modifications:**
   - Generate two random ideas in the `ideas/` folder.
   - Run `git add .` and `git commit -m "Add decoy spawner hazard to spawn fast-moving player mimics"`
   - Call `request_code_review`.
