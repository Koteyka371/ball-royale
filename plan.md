1. **Implement SwarmArena in Python**
   - Add `SwarmArena` class to `src/arena/arena_types.py` inheriting from `ProceduralArena`.
   - Implement `generate` method:
     - Add a huge central battle room with no hazards.
     - Add 4 corner base rooms.
     - Add 8 corridors connecting the corner bases to the central room.
   - Register it in the `ARENAS` dictionary.

2. **Register SwarmArena in GDScript**
   - Add `"swarm"` to the `ARENAS` array in `src/arena/arena_types.gd`.

3. **Verify Creation**
   - Read the python and gdscript files to ensure the modifications were successful.

4. **Add Unit Tests**
   - Create `tests/test_arena_swarm.py` to verify the generated rooms and corridors count, sizes, and point inclusion in the new arena type.

5. **Run all tests**
   - Execute `pytest tests/`

6. **Pre-commit and Idea**
   - Execute pre-commit instructions.
   - Generate a new JSON idea file in `ideas/`.
