1. **Explore `game_modes.py` and `game_modes.gd`**
   - Create a new class `MagneticCollisionsMode` inheriting from `GameMode`.
   - Set name to `"Magnetic Collisions"` and description to `"Collisions pull entities together instead of pushing them apart, creating chaotic clusters of balls that can be targeted by AoE attacks."`
   - In `game_modes.py` and `game_modes.gd`, register `"magnetic_collisions": MagneticCollisionsMode()` in the dict of modes at the bottom of the files.
2. **Explore `action.py` and `action.gd`**
   - In `_resolve_collisions`, check if `self.world.game_mode.name == "Magnetic Collisions"`.
   - If true, `knockback_multiplier = -0.5` (a negative value to pull them together). Let's use `-0.5` as a stable negative multiplier that will pull entities together per frame until they perfectly overlap (distance -> 0).
3. **Write tests**
   - Create `src/ai/test_magnetic_collisions.py` testing the collision resolution pulls them together instead of apart.
4. **Pre commit**
   - Run tests and complete pre-commit instructions.
5. **Submit**
   - Submit the PR.
