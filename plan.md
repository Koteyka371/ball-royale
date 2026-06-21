1. **Understand Task**: Create the "Physics Chain Reactions" arena as described in the game design document. The document says: "9. Physics Chain Reactions — Balls bouncing off walls/enemies create ripple effects. A well-timed bounce can push an enemy into a hazard."
2. **Arena Design**: We need to create an arena called `PhysicsChainArena`. It should be designed specifically to encourage these chain reactions and pushes into hazards.
   - A central "chain reaction" space with walls designed for bouncing.
   - Numerous hazards scattered around so that bouncing enemies pushes them into hazards.
   - We'll create `PhysicsChainArena` inheriting from `ProceduralArena`. We'll populate `self.rooms`, `self.corridors`, and `self.hazards`.
   - Rooms/Corridors overlapping but creating some natural walls to bounce off. E.g., a "pinball" or "billiard" style map with bumpers (small hazards) or walls. Let's make a grid of small hazards.
3. **Registration**:
   - Add `PhysicsChainArena` to `ARENAS` dict in `src/arena/arena_types.py`.
   - Add `"physics_chain"` to `ARENAS` list in `src/arena/arena_types.gd`.
4. **Testing**:
   - Create `tests/test_arena_physics_chain.py` to assert the basic properties of the new arena (rooms, hazards exist, and possibly a simulated bounce).
5. **Ideas File**: Create an idea JSON file in `ideas/`.
6. **Pre-commit**: Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
7. **Submission**: Stage, commit, push branch, create PR.
