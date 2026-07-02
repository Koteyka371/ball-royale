1. **Understand Goal**: Allow spectators (or simulated crowd mechanics) to vote on events, such as which hazard spawns next or which player gets a buff during sudden death, making the arena feel more dynamic and engaged.
2. **Implement Crowd Interaction Mode**: Create a new mode called `CrowdInteractionMode` (or `SpectatorVotingMode`) extending `GameMode` in `src/ai/game_modes.py` and `src/ai/game_modes.gd`.
    - In this mode, a timer tracks voting phases.
    - Every X seconds, a simulated "vote" occurs.
    - Events could include: spawning hazards, granting a random player a buff, applying sudden death rules, spawning an item, changing weather.
    - To keep it simple, we can have 3 event options (e.g., "Spawn Hazard", "Buff Random Player", "Spawn Item").
    - The code will use `random.choices` or similar to "simulate" a crowd vote, or we can just randomly pick one of the options with some weighted probabilities and execute the result.
3. **Add implementation in Python**:
    - Add `CrowdInteractionMode` to `src/ai/game_modes.py`.
    - Register it in `GAME_MODES`.
4. **Add implementation in GDScript**:
    - Add `class CrowdInteractionMode extends GameMode` to `src/ai/game_modes.gd`.
    - Register it in the global registry in GDScript.
5. **Add tests**:
    - Add `test_crowd_interaction_mode` in `tests/test_game_modes.py` (or `src/ai/test_game_modes.py` based on where it's located).
6. **Create Ideas JSON**: Add 2 idea files in `ideas/` directory.
7. **Pre-commit and PR**: Run tests, pre-commit, push, create PR.
