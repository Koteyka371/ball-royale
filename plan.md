1. **Explore & Define Arena Layout**:
   - Define exact dimensions for `BallRelationshipsArena` to satisfy Specificity Rule.
   - For `arena_size = 2000` (`width` & `height`), `cx = 1000`, `cy = 1000`.
   - 4 large spawn rooms at the corners (Rival, Ally, Grudge zones). Room sizes: 300x300.
     - Top-Left: `(100, 100, 300, 300)`
     - Top-Right: `(1600, 100, 300, 300)`
     - Bottom-Left: `(100, 1600, 300, 300)`
     - Bottom-Right: `(1600, 1600, 300, 300)`
   - Central meeting room (where relationships form):
     - Center: `(700, 700, 600, 600)`
   - Corridors (connecting corners to center):
     - Top-Left to Center: `(200, 400, 100, 300)`, `(200, 700, 500, 100)`
     - Top-Right to Center: `(1700, 400, 100, 300)`, `(1300, 700, 500, 100)`
     - Bottom-Left to Center: `(200, 1300, 100, 300)`, `(200, 1200, 500, 100)`
     - Bottom-Right to Center: `(1700, 1300, 100, 300)`, `(1300, 1200, 500, 100)`
   - Hazards in the center to create grudges:
     - Hazard 1: `id=0, x=1000, y=1000, radius=50, kind="lava", damage=20`

2. **Implement in Python (`src/arena/arena_types.py`)**:
   - Create class `BallRelationshipsArena(ProceduralArena)` with `generate` method.
   - Register it in `ARENAS` dictionary as `"ball_relationships"`.

3. **Implement in GDScript (`src/arena/procedural_arena.gd`)**:
   - Create class `BallRelationshipsArena extends ProceduralArena` with `generate` method.

4. **Register in GDScript (`src/arena/arena_types.gd`)**:
   - Add `"ball_relationships"` to `ARENAS` array.

5. **Write Unit Test (`tests/test_ball_relationships_arena.py`)**:
   - Verify `BallRelationshipsArena` layout (rooms and corridors count, overlaps).

6. **Create Ideas File**:
   - Make `ideas/` dir, create `ideas/ball_relationship_idea.json`.

7. **Verify & Pre-Commit**:
   - Run tests.
   - Run `pre_commit_instructions`.

8. **Submit**.
