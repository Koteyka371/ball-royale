1. **Understand Task**: Create hazards that slowly shrink the safe playable area over time, similar to a battle royale zone. This logic exists in game_modes but not generically inside the procedural generation.
2. **Analysis**: We've modified `procedural_arena.py` and `procedural_arena.gd` to include a new hazard type `shrinking_zone` that uses `randf_range`/`random.uniform` to set initial radius, min radius, and shrink rate.
3. **Execution**: We added `shrinking_zone` into the generation table, and handled its ticking properly inside both python and gdscript.
4. **Interaction**: We updated `action.py` and `action.gd` to process damage if players are outside of the `shrinking_zone`'s current radius. (Similar to Battle Royale logic).
5. **Testing**: We patched `test_procedural_arena.py` to include `shrinking_zone` in the hardcoded assertions of test passes.
6. **IDEAS INBOX**: We successfully implemented the two required files `idea_idea-418_1.json` and `idea_idea-418_2.json`.
7. **Verification**: `PYTHONPATH=src pytest` passes, meaning python tests are green. Godot scripts have been updated symmetrically.
8. **Pre-commit**: Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
9. **Submission**: Submit via the `submit` tool to the origin repository on the branch `idea-418`.
