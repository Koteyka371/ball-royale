1. Add `FunnyFailsArena` in `src/arena/arena_types.py`. It should inherit from `ProceduralArena`. Define the `generate(self)` method to create an arena tailored for "Funny fails — шарик падает в ловушку". The layout could include a large central room with several large hazards (like "lava" or "spikes") or multiple rooms connected by narrow corridors with hazards in them to force mistakes. Register it in `ARENAS = { ... "funny_fails": FunnyFailsArena, ... }`.

2. Add `FunnyFailsArena` in `src/arena/arena_types.gd` to mirror the Python version. Include `class FunnyFailsArena extends ProceduralArena: ...` inside `src/arena/procedural_arena.gd` (Wait, in `arena_types.gd` it has a string constant in `ARENAS` array, and the classes are in `procedural_arena.gd` based on my grepping earlier). Yes, I will add `"funny_fails"` to the `ARENAS` array in `arena_types.gd`, and implement the class in `procedural_arena.gd`.

3. Create a test file `tests/test_arena_funny_fails.py` to ensure it generates correctly, similar to `test_clutch_plays_arena.py`.

4. Generate a new feature idea JSON in `ideas/` directory.

5. Pre-commit step and submit.
